import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.factura import Factura, TipoFactura, EstadoFactura
from app.models.cliente import Cliente
from app.services.factura_service import FacturaService
from app.services.notification_service import NotificationService
from app.services.signature_service import SignatureService
from app.schemas.factura import FacturaCreate, FacturaUpdate
from app.database import SessionLocal, engine, Base

@pytest.fixture(scope="module")
def db():
    """Crear sesión de base de datos para pruebas"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def cliente(db):
    """Fixture para crear un cliente de prueba"""
    # Eliminar cualquier cliente existente con el mismo NIF
    db.query(Cliente).filter(Cliente.nif_cif == "12345678Z").delete()
    
    # Eliminar cualquier factura existente
    db.query(Factura).delete()
    
    nuevo_cliente = Cliente(
        nombre="Cliente de Prueba",
        nif_cif="12345678Z",
        email="cliente@ejemplo.com",
        telefono="123456789",
        direccion="Calle Prueba 123",
        codigo_postal="28001",
        ciudad="Madrid",
        provincia="Madrid",
        pais="España"
    )
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    
    return nuevo_cliente

@pytest.fixture
def factura_service(db):
    """Crear un servicio de facturas para pruebas"""
    return FacturaService(
        db, 
        notification_service=NotificationService(config_path="config/notification_config.json"),
        signature_service=SignatureService()
    )

def test_crear_factura(db, factura_service, cliente):
    """Prueba la creación de una factura ordinaria"""
    factura_data = FacturaCreate(
        serie="FACT",
        numero="FACT2024/0001",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=1000.00,
        tipo_iva=21.0,
        concepto="Servicio de prueba",
        tipo=TipoFactura.ordinaria,
        estado=EstadoFactura.borrador
    )
    
    factura = factura_service.crear_factura(factura_data)
    
    assert factura is not None
    assert factura.serie == "FACT"
    assert factura.base_imponible == 1000.00
    assert factura.cuota_iva == 210.00
    assert factura.total_factura == 1210.00

def test_actualizar_factura(db, factura_service, cliente):
    """Prueba la actualización de una factura"""
    # Primero crear una factura
    factura_data = FacturaCreate(
        serie="FACT",
        numero="FACT2024/0002",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=1000.00,
        tipo_iva=21.0,
        concepto="Servicio de prueba",
        tipo=TipoFactura.ordinaria,
        estado=EstadoFactura.borrador
    )
    factura = factura_service.crear_factura(factura_data)
    
    # Actualizar la factura
    update_data = FacturaUpdate(
        base_imponible=1500.00,
        concepto="Servicio de prueba actualizado"
    )
    
    factura_actualizada = factura_service.actualizar_factura(factura.id, update_data)
    
    assert factura_actualizada.base_imponible == 1500.00
    assert factura_actualizada.cuota_iva == 315.00
    assert factura_actualizada.total_factura == 1815.00
    assert factura_actualizada.concepto == "Servicio de prueba actualizado"

def test_obtener_facturas(db, factura_service, cliente):
    """Prueba la obtención de facturas con filtros"""
    # Crear algunas facturas de prueba
    facturas_data = [
        FacturaCreate(
            serie="FACT",
            numero=f"FACT2024/000{i}",
            fecha_expedicion=datetime.now(),
            cliente_id=cliente.id,
            base_imponible=1000.00 * i,
            tipo_iva=21.0,
            concepto=f"Servicio de prueba {i}",
            tipo=TipoFactura.ordinaria,
            estado=EstadoFactura.borrador if i % 2 == 0 else EstadoFactura.emitida
        ) for i in range(1, 4)
    ]
    
    for data in facturas_data:
        factura_service.crear_factura(data)
    
    # Obtener facturas por cliente
    facturas_cliente = factura_service.obtener_facturas(cliente_id=cliente.id)
    assert len(facturas_cliente) >= 3
    
    # Obtener facturas por estado
    facturas_borrador = factura_service.obtener_facturas(estado=EstadoFactura.borrador)
    facturas_emitidas = factura_service.obtener_facturas(estado=EstadoFactura.emitida)
    
    assert len(facturas_borrador) > 0
    assert len(facturas_emitidas) > 0

@pytest.mark.asyncio
async def test_enviar_factura_por_email(db, factura_service, cliente):
    """Prueba el envío de una factura por email"""
    # Crear una factura
    factura_data = FacturaCreate(
        serie="FACT",
        numero="FACT2024/0005",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=1000.00,
        tipo_iva=21.0,
        concepto="Servicio de prueba para email",
        tipo=TipoFactura.ordinaria,
        estado=EstadoFactura.emitida
    )
    factura = factura_service.crear_factura(factura_data)
    
    # Enviar factura por email
    enviada = await factura_service.enviar_factura_por_email(factura.id)
    
    assert enviada is True

@pytest.mark.asyncio
async def test_firmar_factura(db, factura_service, cliente):
    """Prueba la firma digital de una factura"""
    # Crear una factura
    factura_data = FacturaCreate(
        serie="FACT",
        numero="FACT2024/0006",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=1000.00,
        tipo_iva=21.0,
        concepto="Servicio de prueba para firma digital",
        tipo=TipoFactura.ordinaria,
        estado=EstadoFactura.emitida
    )
    factura = factura_service.crear_factura(factura_data)
    
    # Firmar factura
    factura_firmada = await factura_service.firmar_factura(factura.id)
    
    assert factura_firmada is not None
    assert factura_firmada.firma_digital is not None
    assert factura_firmada.xml_content is not None

def test_crear_factura_rectificativa(db, factura_service, cliente):
    """Prueba la creación de una factura rectificativa"""
    # Crear factura original
    factura_original_data = FacturaCreate(
        serie="FACT",
        numero="FACT2024/0007",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=1000.00,
        tipo_iva=21.0,
        concepto="Servicio original",
        tipo=TipoFactura.ordinaria,
        estado=EstadoFactura.emitida
    )
    factura_original = factura_service.crear_factura(factura_original_data)
    
    # Crear factura rectificativa
    factura_rectificativa_data = FacturaCreate(
        serie="RECT",
        numero="RECT2024/0001",
        fecha_expedicion=datetime.now(),
        cliente_id=cliente.id,
        base_imponible=-500.00,  # Rectificación parcial
        tipo_iva=21.0,
        concepto="Rectificación de servicio",
        tipo=TipoFactura.rectificativa,
        estado=EstadoFactura.borrador,
        factura_original_id=factura_original.id,
        motivo_rectificacion="Error en la facturación inicial"
    )
    
    factura_rectificativa = factura_service.crear_factura(factura_rectificativa_data)
    
    assert factura_rectificativa is not None
    assert factura_rectificativa.tipo == TipoFactura.rectificativa
    assert factura_rectificativa.factura_original_id == factura_original.id
    assert factura_rectificativa.base_imponible == -500.00
    assert factura_rectificativa.cuota_iva == -105.00
    assert factura_rectificativa.total_factura == -605.00
