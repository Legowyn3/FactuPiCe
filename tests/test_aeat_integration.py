import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.factura import Factura
from app.models.cliente import Cliente
from app.services.ticketbai_service import TicketBAIService
from app.services.security_service import SecurityService
from app.services.facturae_service import FacturaEService

# Configuración del entorno de pruebas
TEST_CERT_PATH = os.getenv("TEST_CERT_PATH", "tests/resources/aeat_test_cert.p12")
TEST_CERT_PASSWORD = os.getenv("TEST_CERT_PASSWORD", "test_password")

@pytest.fixture
def security_service():
    """Fixture para el servicio de seguridad con certificado de pruebas."""
    return SecurityService(
        cert_path=TEST_CERT_PATH,
        cert_password=TEST_CERT_PASSWORD
    )

@pytest.fixture
def ticketbai_service(security_service):
    """Fixture para el servicio TicketBAI en modo pruebas."""
    return TicketBAIService(security_service, test_mode=True)

@pytest.fixture
def test_client(db: Session):
    """Fixture para crear un cliente de prueba."""
    client = Cliente(
        nif_cif="B00000000",  # NIF de prueba según AEAT
        nombre="Empresa de Prueba, S.L.",
        direccion="Calle de Prueba, 123",
        codigo_postal="28001",
        ciudad="Madrid",
        provincia="Madrid",
        pais="España"
    )
    db.add(client)
    db.commit()
    return client

@pytest.fixture
def test_invoice(db: Session, test_client):
    """Fixture para crear una factura de prueba."""
    invoice = Factura(
        serie="FACT",
        numero="FACT2024/0001",
        fecha_expedicion=datetime.now(),
        cliente_id=test_client.id,
        base_imponible=1000.00,
        tipo_iva=21,
        cuota_iva=210.00,
        total_factura=1210.00,
        concepto="Factura de prueba AEAT",
        estado="borrador"
    )
    db.add(invoice)
    db.commit()
    return invoice

class TestAEATIntegration:
    """Pruebas de integración con los servicios de la AEAT."""

    @pytest.mark.asyncio
    async def test_submit_invoice(self, db: Session, ticketbai_service, test_invoice):
        """Prueba el envío de una factura al entorno de pruebas."""
        result = await ticketbai_service.submit_invoice(test_invoice)
        assert result['success']
        assert result['tbai_identifier']

    @pytest.mark.asyncio
    async def test_invoice_signature(self, security_service, test_invoice):
        """Prueba la firma de factura según especificaciones AEAT."""
        facturae_service = FacturaEService()
        xml_content = await facturae_service.generate_invoice_xml(test_invoice)
        signed_xml, timestamp = await security_service.sign_invoice_xml(xml_content)
        
        assert signed_xml
        assert timestamp
        assert "SignedProperties" in signed_xml.decode()

    @pytest.mark.asyncio
    async def test_cancel_invoice(self, db: Session, ticketbai_service, test_invoice):
        """Prueba la anulación de una factura."""
        # Primero enviamos la factura
        submit_result = await ticketbai_service.submit_invoice(test_invoice)
        assert submit_result['success']
        
        # Luego la anulamos
        cancel_result = await ticketbai_service.cancel_invoice(test_invoice)
        assert cancel_result['success']

    @pytest.mark.asyncio
    async def test_check_invoice_status(self, db: Session, ticketbai_service, test_invoice):
        """Prueba la consulta de estado de una factura."""
        # Primero enviamos la factura
        submit_result = await ticketbai_service.submit_invoice(test_invoice)
        assert submit_result['success']
        
        # Consultamos su estado
        status_result = await ticketbai_service.check_invoice_status(test_invoice)
        assert status_result['success']
        assert 'estado' in status_result

    @pytest.mark.asyncio
    async def test_invoice_chain(self, db: Session, ticketbai_service, test_client):
        """Prueba la cadena de facturas y sus hashes."""
        # Crear serie de facturas
        invoices = []
        for i in range(3):
            invoice = Factura(
                serie="FACT",
                numero=f"FACT2024/{i+1:04d}",
                fecha_expedicion=datetime.now() + timedelta(days=i),
                cliente_id=test_client.id,
                base_imponible=1000.00 * (i+1),
                tipo_iva=21,
                cuota_iva=210.00 * (i+1),
                total_factura=1210.00 * (i+1),
                concepto=f"Factura de prueba AEAT #{i+1}",
                estado="borrador"
            )
            db.add(invoice)
            db.commit()
            
            # Enviar factura
            result = await ticketbai_service.submit_invoice(invoice)
            assert result['success']
            
            # Verificar hash anterior
            if i > 0:
                assert invoice.previous_invoice_hash == invoices[-1].invoice_hash
            
            invoices.append(invoice)

    @pytest.mark.asyncio
    async def test_special_invoice_types(self, db: Session, ticketbai_service, test_client):
        """Prueba diferentes tipos de facturas."""
        # Factura rectificativa
        rect_invoice = Factura(
            serie="RECT",
            numero="RECT2024/0001",
            fecha_expedicion=datetime.now(),
            cliente_id=test_client.id,
            base_imponible=-100.00,
            tipo_iva=21,
            cuota_iva=-21.00,
            total_factura=-121.00,
            concepto="Factura rectificativa de prueba",
            tipo="rectificativa",
            motivo_rectificacion="Error en el importe",
            estado="borrador"
        )
        db.add(rect_invoice)
        db.commit()
        
        result = await ticketbai_service.submit_invoice(rect_invoice)
        assert result['success']
        
        # Factura simplificada
        simp_invoice = Factura(
            serie="SIMP",
            numero="SIMP2024/0001",
            fecha_expedicion=datetime.now(),
            cliente_id=test_client.id,
            base_imponible=50.00,
            tipo_iva=21,
            cuota_iva=10.50,
            total_factura=60.50,
            concepto="Factura simplificada de prueba",
            tipo="simplificada",
            estado="borrador"
        )
        db.add(simp_invoice)
        db.commit()
        
        result = await ticketbai_service.submit_invoice(simp_invoice)
        assert result['success']
