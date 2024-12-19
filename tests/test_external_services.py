import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.integrations.external_services import ExternalIntegrationService

@pytest.fixture
def external_service():
    """Crear instancia de servicio de integración externa"""
    return ExternalIntegrationService(
        api_key='test_api_key', 
        base_url='https://mock-financial-api.com'
    )

@pytest.mark.asyncio
async def test_fetch_market_data(external_service):
    """Prueba obtención de datos de mercado"""
    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'symbol': 'AAPL',
            'price': 150.25,
            'change': 2.5
        })
        mock_get.return_value.__aenter__.return_value = mock_response

        # Ejecutar método
        result = await external_service.fetch_market_data('AAPL')

        # Verificaciones
        assert result['symbol'] == 'AAPL'
        assert 'price' in result
        assert 'change' in result

@pytest.mark.asyncio
async def test_get_economic_indicators(external_service):
    """Prueba obtención de indicadores económicos"""
    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'GDP': 1.2,
            'INFLATION': 2.5,
            'UNEMPLOYMENT': 14.5,
            'INTEREST_RATE': 0.5
        })
        mock_get.return_value.__aenter__.return_value = mock_response

        # Ejecutar método
        result = await external_service.get_economic_indicators('ES')

        # Verificaciones
        assert 'GDP' in result
        assert 'INFLATION' in result
        assert 'UNEMPLOYMENT' in result
        assert 'INTEREST_RATE' in result

@pytest.mark.asyncio
async def test_analyze_financial_health(external_service):
    """Prueba análisis de salud financiera"""
    # Datos financieros de ejemplo
    financial_data = {
        'revenue': 1000000,
        'expenses': 800000,
        'profit_margin': 0.2
    }

    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'financial_health_score': 85,
            'risk_level': 'LOW',
            'recommendations': ['Maintain current strategy']
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        # Ejecutar método
        result = await external_service.analyze_financial_health(financial_data)

        # Verificaciones
        assert 'financial_health_score' in result
        assert 'risk_level' in result
        assert 'recommendations' in result

@pytest.mark.asyncio
async def test_get_credit_risk_score(external_service):
    """Prueba obtención de puntuación de riesgo crediticio"""
    # Datos de empresa de ejemplo
    company_data = {
        'annual_revenue': 5000000,
        'years_in_business': 5,
        'debt_ratio': 0.4
    }

    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'credit_risk_score': 75
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        # Ejecutar método
        result = await external_service.get_credit_risk_score(company_data)

        # Verificaciones
        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

@pytest.mark.asyncio
async def test_batch_external_analysis(external_service):
    """Prueba análisis por lotes"""
    # Datos de empresas de ejemplo
    companies = [
        {'name': 'Empresa A', 'revenue': 1000000},
        {'name': 'Empresa B', 'revenue': 2000000}
    ]

    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'financial_health_score': 80
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        # Ejecutar método
        results = await external_service.batch_external_analysis(companies)

        # Verificaciones
        assert len(results) == len(companies)
        assert all('financial_health_score' in result for result in results)

def test_validate_api_key(external_service):
    """Prueba validación de clave API"""
    # Mockear la respuesta HTTP
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Caso de éxito
        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response_success

        assert external_service.validate_api_key() is True

        # Caso de fallo
        mock_response_failure = AsyncMock()
        mock_response_failure.status = 401
        mock_get.return_value.__aenter__.return_value = mock_response_failure

        assert external_service.validate_api_key() is False
