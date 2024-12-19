import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.services.financial_recommendations_service import FinancialRecommendationsService
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.integrations.external_services import ExternalIntegrationService

# Crear Base para modelos de prueba
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
    mock_service.get_economic_indicators = AsyncMock(return_value={
        'INFLATION': 3.5,
        'INTEREST_RATE': 2.0
    })
    return mock_service

@pytest.mark.asyncio
async def test_generate_business_recommendations(db_session, mock_external_service):
    """Probar generación de recomendaciones de negocio"""
    # Preparar datos de prueba
    cliente1 = Cliente(nombre="Empresa A")
    cliente2 = Cliente(nombre="Empresa B")
    db_session.add_all([cliente1, cliente2])
    
    facturas = [
        Factura(
            cliente=cliente1, 
            total_factura=1000, 
            base_imponible=800, 
            cuota_iva=200, 
            tipo="SERVICIO",
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente=cliente1, 
            total_factura=1500, 
            base_imponible=1200, 
            cuota_iva=300, 
            tipo="PRODUCTO",
            fecha_expedicion=datetime.now() - timedelta(days=60)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Crear servicio de recomendaciones
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Ejecutar generación de recomendaciones
    recommendations = await recommendations_service.generate_business_recommendations()

    # Verificaciones
    assert 'revenue_optimization' in recommendations
    assert 'client_segmentation' in recommendations
    assert 'cost_efficiency' in recommendations
    assert 'investment_suggestions' in recommendations

@pytest.mark.asyncio
async def test_client_specific_insights(db_session, mock_external_service):
    """Probar generación de insights específicos de cliente"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    
    facturas = [
        Factura(
            cliente=cliente, 
            total_factura=1000, 
            base_imponible=800, 
            cuota_iva=200, 
            tipo="SERVICIO",
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente=cliente, 
            total_factura=1500, 
            base_imponible=1200, 
            cuota_iva=300, 
            tipo="PRODUCTO",
            fecha_expedicion=datetime.now() - timedelta(days=60)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Crear servicio de recomendaciones
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Ejecutar generación de insights personalizados
    insights = await recommendations_service.generate_personalized_financial_insights(cliente.id)

    # Verificaciones
    assert 'general_recommendations' in insights
    assert 'personalized_insights' in insights
    assert insights['personalized_insights']['client_name'] == "Empresa Test"
    assert insights['personalized_insights']['total_invoices'] == 2

@pytest.mark.asyncio
async def test_investment_recommendations(db_session, mock_external_service):
    """Probar recomendaciones de inversión"""
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Ejecutar generación de recomendaciones de inversión
    investment_recommendations = await recommendations_service._investment_recommendations()

    # Verificaciones
    assert len(investment_recommendations) > 0
    assert investment_recommendations[0]['type'] == 'INVESTMENT_STRATEGY'
    assert 'suggested_actions' in investment_recommendations[0]

@pytest.mark.asyncio
async def test_external_service_error_handling(db_session):
    """Probar manejo de errores en servicio externo"""
    # Mock de servicio externo que lanza excepción
    mock_service = MagicMock(spec=ExternalIntegrationService)
    mock_service.get_economic_indicators = AsyncMock(side_effect=Exception("Error de conexión"))

    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_service
    )

    # Ejecutar generación de recomendaciones de inversión
    investment_recommendations = await recommendations_service._investment_recommendations()

    # Verificaciones
    assert len(investment_recommendations) > 0
    assert investment_recommendations[0]['type'] == 'INVESTMENT_ANALYSIS_ERROR'
    assert 'Error de conexión' in investment_recommendations[0]['error']

@pytest.mark.asyncio
async def test_revenue_optimization_recommendations(db_session, mock_external_service):
    """Probar recomendaciones específicas de optimización de ingresos"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    
    facturas = [
        Factura(
            cliente=cliente, 
            total_factura=500, 
            base_imponible=400, 
            cuota_iva=100, 
            tipo="SERVICIO",
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente=cliente, 
            total_factura=300, 
            base_imponible=250, 
            cuota_iva=50, 
            tipo="SERVICIO",
            fecha_expedicion=datetime.now() - timedelta(days=60)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Crear servicio de recomendaciones
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Ejecutar método privado de optimización de ingresos
    revenue_recommendations = await recommendations_service._revenue_optimization_recommendations()

    # Verificaciones
    assert len(revenue_recommendations) > 0
    assert any(rec['type'] == 'REVENUE_GROWTH' or rec['type'] == 'INVOICE_DIVERSIFICATION' for rec in revenue_recommendations)

@pytest.mark.asyncio
async def test_cost_efficiency_recommendations(db_session, mock_external_service):
    """Probar recomendaciones de eficiencia de costos"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Empresa Test")
    db_session.add(cliente)
    
    facturas = [
        Factura(
            cliente=cliente, 
            total_factura=1000, 
            base_imponible=700, 
            cuota_iva=300, 
            tipo="SERVICIO",
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente=cliente, 
            total_factura=800, 
            base_imponible=600, 
            cuota_iva=200, 
            tipo="PRODUCTO",
            fecha_expedicion=datetime.now() - timedelta(days=60)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Crear servicio de recomendaciones
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Ejecutar método privado de eficiencia de costos
    cost_recommendations = await recommendations_service._cost_efficiency_recommendations()

    # Verificaciones
    assert isinstance(cost_recommendations, list)

@pytest.mark.asyncio
async def test_nonexistent_client_insights(db_session, mock_external_service):
    """Probar generación de insights para cliente no existente"""
    # Crear servicio de recomendaciones
    recommendations_service = FinancialRecommendationsService(
        db=db_session, 
        external_service=mock_external_service
    )

    # Intentar obtener insights para cliente no existente
    insights = await recommendations_service.generate_personalized_financial_insights(client_id=9999)

    # Verificaciones
    assert 'general_recommendations' in insights
    assert 'personalized_insights' in insights
    assert insights['personalized_insights'] == {}

# Configuración de pytest para tests asíncronos
import asyncio
import pytest

def pytest_configure(config):
    """Configuración de pytest para manejar tests asíncronos"""
    config.addinivalue_line(
        "markers", "asyncio: mark test to run with asyncio"
    )

def pytest_make_collect_report(collector):
    """Manejar colección de tests asíncronos"""
    if hasattr(collector, 'collect'):
        collector.collect()
