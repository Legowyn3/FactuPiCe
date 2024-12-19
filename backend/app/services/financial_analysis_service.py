import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract

from ..models.factura import Factura
from ..models.cliente import Cliente
from ..schemas.factura import TipoFactura

class FinancialAnalysisService:
    def __init__(self, db: Session):
        self.db = db

    async def get_financial_dashboard(self, 
                                      start_date: Optional[datetime] = None, 
                                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera un dashboard completo de análisis financiero.
        
        Args:
            start_date (Optional[datetime]): Fecha de inicio para el análisis
            end_date (Optional[datetime]): Fecha de fin para el análisis
        
        Returns:
            Dict con métricas financieras detalladas
        """
        # Si no se proporcionan fechas, usar los últimos 12 meses
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()

        # Ejecutar consultas en paralelo para mejorar rendimiento
        tasks = [
            self._total_revenue(start_date, end_date),
            self._revenue_by_invoice_type(start_date, end_date),
            self._top_clients_by_revenue(start_date, end_date),
            self._monthly_revenue_trend(start_date, end_date),
            self._tax_analysis(start_date, end_date),
            self._invoice_count_trend(start_date, end_date)
        ]

        results = await asyncio.gather(*tasks)

        return {
            'total_revenue': results[0],
            'revenue_by_invoice_type': results[1],
            'top_clients': results[2],
            'monthly_revenue_trend': results[3],
            'tax_analysis': results[4],
            'invoice_count_trend': results[5]
        }

    async def _total_revenue(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Calcula los ingresos totales y métricas relacionadas."""
        total_revenue_query = self.db.query(
            func.sum(Factura.total_factura).label('total_revenue'),
            func.avg(Factura.total_factura).label('average_invoice_value'),
            func.count(Factura.id).label('total_invoices')
        ).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).one()

        return {
            'total': total_revenue_query.total_revenue or 0,
            'average_invoice_value': total_revenue_query.average_invoice_value or 0,
            'total_invoices': total_revenue_query.total_invoices or 0
        }

    async def _revenue_by_invoice_type(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Analiza ingresos por tipo de factura."""
        revenue_by_type = self.db.query(
            Factura.tipo,
            func.sum(Factura.total_factura).label('total_revenue')
        ).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).group_by(Factura.tipo).all()

        return {str(tipo): revenue for tipo, revenue in revenue_by_type}

    async def _top_clients_by_revenue(self, start_date: datetime, end_date: datetime, top_n: int = 5) -> List[Dict[str, Any]]:
        """Obtiene los clientes top por ingresos."""
        top_clients = self.db.query(
            Cliente.id,
            Cliente.nombre,
            func.sum(Factura.total_factura).label('total_revenue'),
            func.count(Factura.id).label('total_invoices')
        ).join(Factura, Cliente.id == Factura.cliente_id).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).group_by(Cliente.id, Cliente.nombre).order_by(
            func.sum(Factura.total_factura).desc()
        ).limit(top_n).all()

        return [
            {
                'client_id': client_id,
                'name': name,
                'total_revenue': total_revenue,
                'total_invoices': total_invoices
            } for client_id, name, total_revenue, total_invoices in top_clients
        ]

    async def _monthly_revenue_trend(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Genera tendencia de ingresos mensuales."""
        monthly_revenue = self.db.query(
            extract('year', Factura.fecha_expedicion).label('year'),
            extract('month', Factura.fecha_expedicion).label('month'),
            func.sum(Factura.total_factura).label('total_revenue')
        ).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).group_by('year', 'month').order_by('year', 'month').all()

        return [
            {
                'year': int(year),
                'month': int(month),
                'total_revenue': total_revenue
            } for year, month, total_revenue in monthly_revenue
        ]

    async def _tax_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Análisis detallado de impuestos."""
        tax_analysis = self.db.query(
            Factura.tipo_iva,
            func.sum(Factura.base_imponible).label('total_base'),
            func.sum(Factura.cuota_iva).label('total_tax')
        ).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).group_by(Factura.tipo_iva).all()

        return {
            str(tipo_iva): {
                'total_base': total_base,
                'total_tax': total_tax
            } for tipo_iva, total_base, total_tax in tax_analysis
        }

    async def _invoice_count_trend(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Tendencia de número de facturas."""
        invoice_count_trend = self.db.query(
            extract('year', Factura.fecha_expedicion).label('year'),
            extract('month', Factura.fecha_expedicion).label('month'),
            func.count(Factura.id).label('total_invoices')
        ).filter(
            Factura.fecha_expedicion.between(start_date, end_date)
        ).group_by('year', 'month').order_by('year', 'month').all()

        return [
            {
                'year': int(year),
                'month': int(month),
                'total_invoices': total_invoices
            } for year, month, total_invoices in invoice_count_trend
        ]

    async def predict_future_revenue(self, 
                                     historical_months: int = 12, 
                                     prediction_months: int = 3) -> Dict[str, Any]:
        """
        Predice ingresos futuros basándose en datos históricos.
        Usa un método simple de promedio móvil.
        
        Args:
            historical_months (int): Meses de datos históricos a considerar
            prediction_months (int): Meses a predecir
        
        Returns:
            Predicción de ingresos futuros
        """
        # Obtener datos históricos
        end_date = datetime.now()
        start_date = end_date - timedelta(days=historical_months * 30)

        monthly_revenue = await self._monthly_revenue_trend(start_date, end_date)

        # Calcular promedio móvil
        if len(monthly_revenue) < historical_months:
            return {"error": "Datos históricos insuficientes"}

        # Tomar los últimos 'historical_months' meses
        recent_revenues = [month['total_revenue'] for month in monthly_revenue[-historical_months:]]
        average_revenue = sum(recent_revenues) / len(recent_revenues)

        # Predecir próximos meses
        predictions = [
            {
                'month': (end_date + timedelta(days=30*i)).month,
                'year': (end_date + timedelta(days=30*i)).year,
                'predicted_revenue': average_revenue
            } for i in range(1, prediction_months + 1)
        ]

        return {
            'average_historical_revenue': average_revenue,
            'predictions': predictions
        }

    async def advanced_revenue_prediction(self, 
                                          historical_months: int = 12, 
                                          prediction_months: int = 3,
                                          model_type: str = 'exponential_smoothing') -> Dict[str, Any]:
        """
        Predicción de ingresos avanzada con múltiples modelos.
        
        Args:
            historical_months (int): Meses de datos históricos
            prediction_months (int): Meses a predecir
            model_type (str): Tipo de modelo de predicción
        
        Returns:
            Predicción de ingresos con múltiples modelos
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=historical_months * 30)

        monthly_revenue = await self._monthly_revenue_trend(start_date, end_date)

        if len(monthly_revenue) < historical_months:
            return {"error": "Datos históricos insuficientes"}

        revenues = [month['total_revenue'] for month in monthly_revenue]

        if model_type == 'exponential_smoothing':
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            import numpy as np

            model = ExponentialSmoothing(
                revenues, 
                trend='add', 
                seasonal='add', 
                seasonal_periods=12
            ).fit()

            forecast = model.forecast(steps=prediction_months)
            
            predictions = [
                {
                    'month': (end_date + timedelta(days=30*i)).month,
                    'year': (end_date + timedelta(days=30*i)).year,
                    'predicted_revenue': float(pred),
                    'confidence_interval': {
                        'lower': float(pred * 0.9),
                        'upper': float(pred * 1.1)
                    }
                } for i, pred in enumerate(forecast, 1)
            ]

        elif model_type == 'arima':
            from statsmodels.tsa.arima.model import ARIMA
            
            model = ARIMA(revenues, order=(1,1,1)).fit()
            forecast = model.forecast(steps=prediction_months)
            
            predictions = [
                {
                    'month': (end_date + timedelta(days=30*i)).month,
                    'year': (end_date + timedelta(days=30*i)).year,
                    'predicted_revenue': float(pred),
                    'confidence_interval': {
                        'lower': float(pred * 0.85),
                        'upper': float(pred * 1.15)
                    }
                } for i, pred in enumerate(forecast, 1)
            ]

        else:
            # Método de promedio móvil por defecto
            average_revenue = sum(revenues[-historical_months:]) / len(revenues[-historical_months:])
            
            predictions = [
                {
                    'month': (end_date + timedelta(days=30*i)).month,
                    'year': (end_date + timedelta(days=30*i)).year,
                    'predicted_revenue': average_revenue,
                    'confidence_interval': {
                        'lower': average_revenue * 0.9,
                        'upper': average_revenue * 1.1
                    }
                } for i in range(1, prediction_months + 1)
            ]

        return {
            'model_type': model_type,
            'historical_data': monthly_revenue,
            'predictions': predictions,
            'average_historical_revenue': sum(revenues) / len(revenues)
        }

    async def risk_analysis(self, 
                             start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Análisis de riesgo financiero.
        
        Args:
            start_date (Optional[datetime]): Fecha de inicio
            end_date (Optional[datetime]): Fecha de fin
        
        Returns:
            Análisis de riesgos financieros
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()

        # Análisis de concentración de clientes
        top_clients = await self._top_clients_by_revenue(start_date, end_date, top_n=10)
        
        # Calcular concentración de ingresos
        total_revenue = sum(client['total_revenue'] for client in top_clients)
        concentration_metrics = [
            {
                'client': client['name'],
                'revenue_share': (client['total_revenue'] / total_revenue) * 100,
                'invoice_count': client['total_invoices']
            } for client in top_clients
        ]

        # Análisis de variabilidad de ingresos
        monthly_revenue = await self._monthly_revenue_trend(start_date, end_date)
        revenue_volatility = self._calculate_revenue_volatility(monthly_revenue)

        # Análisis de tipos de factura
        revenue_by_type = await self._revenue_by_invoice_type(start_date, end_date)

        return {
            'client_concentration': {
                'metrics': concentration_metrics,
                'herfindahl_index': self._calculate_herfindahl_index(concentration_metrics)
            },
            'revenue_volatility': revenue_volatility,
            'revenue_by_invoice_type': revenue_by_type,
            'risk_score': self._calculate_risk_score(
                concentration_metrics, 
                revenue_volatility, 
                revenue_by_type
            )
        }

    def _calculate_revenue_volatility(self, monthly_revenue):
        """Calcular volatilidad de ingresos"""
        import numpy as np
        
        revenues = [month['total_revenue'] for month in monthly_revenue]
        
        return {
            'standard_deviation': float(np.std(revenues)),
            'coefficient_of_variation': float(np.std(revenues) / np.mean(revenues)) if np.mean(revenues) != 0 else 0
        }

    def _calculate_herfindahl_index(self, concentration_metrics):
        """
        Calcular índice Herfindahl-Hirschman para concentración de mercado.
        Valores:
        - 0-1500: Baja concentración
        - 1500-2500: Concentración moderada
        - +2500: Alta concentración
        """
        return sum((metric['revenue_share'] ** 2) for metric in concentration_metrics)

    def _calculate_risk_score(self, 
                               concentration_metrics, 
                               revenue_volatility, 
                               revenue_by_invoice_type):
        """
        Calcular puntuación de riesgo compuesta.
        
        Factores:
        - Concentración de clientes
        - Volatilidad de ingresos
        - Diversificación de tipos de factura
        """
        # Puntuación de concentración de clientes
        top_client_share = concentration_metrics[0]['revenue_share'] if concentration_metrics else 0
        concentration_score = min(top_client_share * 2, 100)  # Máximo 100

        # Puntuación de volatilidad
        volatility_score = min(
            (revenue_volatility['coefficient_of_variation'] * 100), 
            100
        )

        # Puntuación de diversificación
        invoice_type_count = len(revenue_by_invoice_type)
        diversification_score = min(invoice_type_count * 20, 100)  # Máximo 100

        # Calcular puntuación de riesgo compuesta
        risk_score = (
            concentration_score * 0.4 +  # 40% concentración
            volatility_score * 0.3 +     # 30% volatilidad
            (100 - diversification_score) * 0.3  # 30% falta de diversificación
        )

        return {
            'total_risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'components': {
                'client_concentration': concentration_score,
                'revenue_volatility': volatility_score,
                'diversification': diversification_score
            }
        }

    def _get_risk_level(self, risk_score):
        """Determinar nivel de riesgo"""
        if risk_score < 30:
            return 'BAJO'
        elif risk_score < 60:
            return 'MEDIO'
        else:
            return 'ALTO'

    def generate_financial_report(self, 
                                  start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera un informe financiero detallado con análisis de riesgo.
        
        Args:
            start_date (Optional[datetime]): Fecha de inicio
            end_date (Optional[datetime]): Fecha de fin
        
        Returns:
            Informe financiero completo
        """
        # Ejecutar análisis de manera síncrona para informe
        dashboard = asyncio.run(self.get_financial_dashboard(start_date, end_date))
        
        # Añadir análisis predictivo avanzado
        future_revenue = asyncio.run(self.advanced_revenue_prediction())
        
        # Añadir análisis de riesgo
        risk_analysis = asyncio.run(self.risk_analysis(start_date, end_date))
        
        return {
            'dashboard': dashboard,
            'future_revenue_prediction': future_revenue,
            'risk_analysis': risk_analysis
        }
