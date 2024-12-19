import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, MagicMock

from app.services.financial_alerts_service import FinancialAlertService
from app.core.notification_manager import NotificationManager
from app.models.factura import Factura
from app.models.cliente import Cliente
from app.core.database import SessionLocal

@pytest.fixture
def db_session():
    """Crear una sesión de base de datos para pruebas"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def notification_manager():
    """Mock del gestor de notificaciones"""
    return MagicMock(spec=NotificationManager)

@pytest.fixture
def financial_alerts_service(db_session, notification_manager):
    """Crear instancia del servicio de alertas financieras"""
    return FinancialAlertService(db_session, notification_manager)

@pytest.mark.asyncio
async def test_revenue_alerts(financial_alerts_service, db_session, notification_manager):
    """Prueba generación de alertas de ingresos"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    # Crear facturas con patrón de caída de ingresos
    facturas = [
        Factura(
            cliente_id=cliente.id, 
            total_factura=1000.0,
            fecha_expedicion=datetime.now() - timedelta(days=90)
        ),
        Factura(
            cliente_id=cliente.id, 
            total_factura=500.0,  # Caída significativa
            fecha_expedicion=datetime.now() - timedelta(days=30)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Configurar mock de notificaciones
    notification_manager.send_notification = AsyncMock()

    # Ejecutar generación de alertas
    alerts = await financial_alerts_service.generate_financial_alerts()

    # Verificar alertas de ingresos
    revenue_alerts = alerts['revenue_alerts']
    assert len(revenue_alerts) > 0
    assert any(alert['type'] in ['REVENUE_DROP', 'REVENUE_DEVIATION'] for alert in revenue_alerts)

    # Verificar que se enviaron notificaciones
    notification_manager.send_notification.assert_called()

@pytest.mark.asyncio
async def test_client_alerts(financial_alerts_service, db_session, notification_manager):
    """Prueba generación de alertas de clientes"""
    # Preparar clientes con diferentes estados
    clientes = [
        Cliente(nombre="Cliente Activo"),
        Cliente(nombre="Cliente Inactivo")
    ]
    db_session.add_all(clientes)
    db_session.flush()

    # Facturas para cliente activo
    facturas_activo = [
        Factura(
            cliente_id=clientes[0].id, 
            total_factura=1000.0,
            fecha_expedicion=datetime.now() - timedelta(days=15)
        )
    ]

    # Facturas para cliente inactivo (más de 6 meses sin facturas)
    facturas_inactivo = [
        Factura(
            cliente_id=clientes[1].id, 
            total_factura=500.0,
            fecha_expedicion=datetime.now() - timedelta(days=240)
        )
    ]

    db_session.add_all(facturas_activo + facturas_inactivo)
    db_session.commit()

    # Configurar mock de notificaciones
    notification_manager.send_notification = AsyncMock()

    # Ejecutar generación de alertas
    alerts = await financial_alerts_service.generate_financial_alerts()

    # Verificar alertas de clientes
    client_alerts = alerts['client_alerts']
    assert len(client_alerts) > 0
    assert any(alert['type'] in ['INACTIVE_CLIENTS', 'CLIENT_CONCENTRATION'] for alert in client_alerts)

    # Verificar que se enviaron notificaciones
    notification_manager.send_notification.assert_called()

@pytest.mark.asyncio
async def test_invoice_alerts(financial_alerts_service, db_session, notification_manager):
    """Prueba generación de alertas de facturas"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    # Facturas pendientes de pago
    facturas = [
        Factura(
            cliente_id=cliente.id, 
            total_factura=1000.0,
            estado='PENDIENTE',
            fecha_expedicion=datetime.now() - timedelta(days=45)  # Más de 30 días
        ),
        Factura(
            cliente_id=cliente.id, 
            total_factura=500.0,
            tipo='RECTIFICATIVA',
            fecha_expedicion=datetime.now() - timedelta(days=30)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Configurar mock de notificaciones
    notification_manager.send_notification = AsyncMock()

    # Ejecutar generación de alertas
    alerts = await financial_alerts_service.generate_financial_alerts()

    # Verificar alertas de facturas
    invoice_alerts = alerts['invoice_alerts']
    assert len(invoice_alerts) > 0
    assert any(alert['type'] in ['UNPAID_INVOICES', 'HIGH_RECTIFICATIVE_INVOICES'] for alert in invoice_alerts)

    # Verificar que se enviaron notificaciones
    notification_manager.send_notification.assert_called()

@pytest.mark.asyncio
async def test_risk_alerts(financial_alerts_service, db_session, notification_manager):
    """Prueba generación de alertas de riesgo"""
    # Preparar datos de prueba con alto riesgo
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    # Crear facturas con alta variabilidad
    facturas = [
        Factura(
            cliente_id=cliente.id, 
            total_factura=1000.0,
            fecha_expedicion=datetime.now() - timedelta(days=90)
        ),
        Factura(
            cliente_id=cliente.id, 
            total_factura=3000.0,  # Alta variabilidad
            fecha_expedicion=datetime.now() - timedelta(days=30)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Configurar mock de notificaciones
    notification_manager.send_notification = AsyncMock()

    # Ejecutar generación de alertas
    alerts = await financial_alerts_service.generate_financial_alerts()

    # Verificar alertas de riesgo
    risk_alerts = alerts['risk_alerts']
    assert len(risk_alerts) > 0
    assert any(alert['type'] in ['HIGH_RISK_LEVEL', 'HIGH_REVENUE_VOLATILITY'] for alert in risk_alerts)

    # Verificar que se enviaron notificaciones
    notification_manager.send_notification.assert_called()

def test_schedule_financial_alerts(financial_alerts_service, notification_manager):
    """Prueba programación de alertas financieras"""
    # Configurar mock de generación de alertas
    financial_alerts_service.generate_financial_alerts = AsyncMock()
    
    # Configurar mock de notificaciones
    notification_manager.send_notification = AsyncMock()

    # Ejecutar prueba de programación de alertas
    async def test_scheduling():
        await financial_alerts_service.schedule_financial_alerts(interval_hours=1)

    # Verificar que se puede programar sin errores
    import asyncio
    try:
        asyncio.run(asyncio.wait_for(test_scheduling(), timeout=2))
    except asyncio.TimeoutError:
        # Es normal que se agote el tiempo, solo queremos verificar que no haya errores
        pass

    # Verificar que se llamó a generar alertas
    financial_alerts_service.generate_financial_alerts.assert_called()
