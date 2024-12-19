import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.services.financial_alert_service import FinancialAlertService
from app.models.financial_alert import FinancialAlert, AlertType, AlertSeverity
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.services.financial_analysis_service import FinancialAnalysisService
from app.integrations.external_services import ExternalIntegrationService

Base = declarative_base()

@pytest.fixture
def db_session():
    """Crear sesión de base de datos de prueba"""
    engine = create_engine('sqlite:///:memory:')
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def mock_external_service():
    """Mock del servicio de integración externa"""
    mock_service = MagicMock(spec=ExternalIntegrationService)
    mock_service.get_credit_risk_score = AsyncMock(return_value=600)
    mock_service.get_economic_indicators = AsyncMock(return_value={
        'INFLATION': 3.5,
        'INTEREST_RATE': 2.0
    })
    return mock_service

@pytest.mark.asyncio
async def test_generate_client_alerts(db_session, mock_external_service):
    """Probar generación de alertas para un cliente"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    db_session.commit()

    # Crear facturas con diferentes características
    facturas = [
        Factura(
            cliente=cliente, 
            total_factura=5000, 
            base_imponible=4000, 
            cuota_iva=1000, 
            tipo="SERVICIO",
            estado_pago='PENDIENTE',
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente=cliente, 
            total_factura=3000, 
            base_imponible=2500, 
            cuota_iva=500, 
            tipo="PRODUCTO",
            estado_pago='PENDIENTE',
            fecha_expedicion=datetime.now() - timedelta(days=60)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Crear servicio de alertas
    alert_service = FinancialAlertService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Generar alertas
    alerts = await alert_service.generate_client_alerts(cliente.id)

    # Verificaciones
    assert len(alerts) > 0
    assert any(alert.type == AlertType.CASH_FLOW for alert in alerts)
    assert any(alert.type == AlertType.CREDIT_RISK for alert in alerts)

@pytest.mark.asyncio
async def test_save_and_retrieve_alerts(db_session, mock_external_service):
    """Probar guardado y recuperación de alertas"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    db_session.commit()

    # Crear servicio de alertas
    alert_service = FinancialAlertService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Generar alertas
    alerts = await alert_service.generate_client_alerts(cliente.id)

    # Guardar alertas
    alert_service.save_alerts(alerts)

    # Recuperar alertas activas
    active_alerts = await alert_service.get_active_alerts(client_id=cliente.id)

    # Verificaciones
    assert len(active_alerts) > 0
    assert all(alert.is_active for alert in active_alerts)

@pytest.mark.asyncio
async def test_alert_severity_filtering(db_session, mock_external_service):
    """Probar filtrado de alertas por severidad"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    db_session.commit()

    # Crear servicio de alertas con mock de servicio externo que genera alerta crítica
    mock_service = MagicMock(spec=ExternalIntegrationService)
    mock_service.get_credit_risk_score = AsyncMock(return_value=300)  # Muy bajo
    mock_service.get_economic_indicators = AsyncMock(return_value={
        'INFLATION': 7.0,  # Muy alta
        'INTEREST_RATE': 2.0
    })

    alert_service = FinancialAlertService(
        db=db_session, 
        external_service=mock_service
    )

    # Generar alertas
    alerts = await alert_service.generate_client_alerts(cliente.id)
    alert_service.save_alerts(alerts)

    # Recuperar alertas de alta severidad
    high_severity_alerts = await alert_service.get_active_alerts(
        client_id=cliente.id, 
        severity=AlertSeverity.HIGH
    )

    # Verificaciones
    assert len(high_severity_alerts) > 0
    assert all(alert.severity == AlertSeverity.HIGH for alert in high_severity_alerts)

@pytest.mark.asyncio
async def test_external_service_error_handling(db_session):
    """Probar manejo de errores en servicios externos"""
    # Mock de servicio externo que lanza excepción
    mock_service = MagicMock(spec=ExternalIntegrationService)
    mock_service.get_credit_risk_score = AsyncMock(side_effect=Exception("Error de conexión"))
    mock_service.get_economic_indicators = AsyncMock(side_effect=Exception("Error de conexión"))

    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    db_session.commit()

    # Crear servicio de alertas
    alert_service = FinancialAlertService(
        db=db_session, 
        external_service=mock_service
    )

    # Generar alertas
    alerts = await alert_service.generate_client_alerts(cliente.id)

    # Verificaciones
    assert len(alerts) > 0
    assert any(alert.type in [AlertType.CREDIT_RISK, AlertType.MARKET_TREND] for alert in alerts)
    assert any('Error' in alert.description for alert in alerts)
