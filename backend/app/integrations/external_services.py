import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging

class ExternalIntegrationService:
    """
    Servicio de integración con servicios financieros y de análisis externos.
    """
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 base_url: str = 'https://api.financial-services.com'):
        """
        Inicializar servicio de integración.
        
        Args:
            api_key (Optional[str]): Clave de API para servicios externos
            base_url (str): URL base de los servicios
        """
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def fetch_market_data(
        self, 
        symbol: str, 
        data_type: str = 'stock', 
        period: str = 'daily'
    ) -> Dict[str, Any]:
        """
        Obtener datos de mercado para un símbolo específico.
        
        Args:
            symbol (str): Símbolo del activo
            data_type (str): Tipo de dato (stock, crypto, etc.)
            period (str): Periodo de datos
        
        Returns:
            Dict con datos de mercado
        """
        url = f"{self.base_url}/market-data"
        
        params = {
            'symbol': symbol,
            'type': data_type,
            'period': period
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Error fetching market data: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"Exception in fetch_market_data: {e}")
            return {}

    async def get_economic_indicators(
        self, 
        country: str = 'ES', 
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Obtener indicadores económicos para un país.
        
        Args:
            country (str): Código de país
            indicators (Optional[List[str]]): Lista de indicadores a obtener
        
        Returns:
            Dict con indicadores económicos
        """
        url = f"{self.base_url}/economic-indicators"
        
        params = {
            'country': country,
            'indicators': indicators or [
                'GDP', 
                'INFLATION', 
                'UNEMPLOYMENT', 
                'INTEREST_RATE'
            ]
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Error fetching economic indicators: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"Exception in get_economic_indicators: {e}")
            return {}

    async def analyze_financial_health(
        self, 
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analizar salud financiera usando un servicio externo.
        
        Args:
            financial_data (Dict): Datos financieros a analizar
        
        Returns:
            Dict con análisis de salud financiera
        """
        url = f"{self.base_url}/financial-health-analysis"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=financial_data, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Error analyzing financial health: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"Exception in analyze_financial_health: {e}")
            return {}

    async def get_credit_risk_score(
        self, 
        company_data: Dict[str, Any]
    ) -> float:
        """
        Obtener puntuación de riesgo crediticio.
        
        Args:
            company_data (Dict): Datos de la empresa
        
        Returns:
            Puntuación de riesgo crediticio
        """
        url = f"{self.base_url}/credit-risk-score"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=company_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('credit_risk_score', 0)
                    else:
                        self.logger.error(f"Error getting credit risk score: {response.status}")
                        return 0
        except Exception as e:
            self.logger.error(f"Exception in get_credit_risk_score: {e}")
            return 0

    async def batch_external_analysis(
        self, 
        companies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Realizar análisis por lotes para múltiples empresas.
        
        Args:
            companies (List[Dict]): Lista de datos de empresas
        
        Returns:
            Lista de resultados de análisis
        """
        # Ejecutar análisis en paralelo
        tasks = [
            self.analyze_financial_health(company) 
            for company in companies
        ]
        
        results = await asyncio.gather(*tasks)
        
        return results

    def validate_api_key(self) -> bool:
        """
        Validar la clave de API con el servicio externo.
        
        Returns:
            bool: True si la clave es válida, False en caso contrario
        """
        async def _validate():
            url = f"{self.base_url}/validate-api-key"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        return response.status == 200
            except Exception:
                return False
        
        return asyncio.run(_validate())
