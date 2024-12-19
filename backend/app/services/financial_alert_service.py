import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.financial_alert import FinancialAlert, AlertType, AlertSeverity
from app.models.cliente import Cliente
from app.models.factura import Factura
from app.services.financial_analysis_service import FinancialAnalysisService
from app.integrations.external_services import ExternalIntegrationService

class FinancialAlertService:
    def __init__(
        self, 
        db: Session, 
        financial_analysis_service: Optional[FinancialAnalysisService] = None,
        external_service: Optional[ExternalIntegrationService] = None
    ):
        """
        Inicializa el servicio de alertas financieras.
        
        Args:
            db (Session): Sesión de base de datos
            financial_analysis_service (Optional[FinancialAnalysisService]): 
                Servicio de análisis financiero
            external_service (Optional[ExternalIntegrationService]): 
                Servicio de integración externa
        """
        self.db = db
        self.financial_analysis_service = financial_analysis_service or FinancialAnalysisService(db)
        self.external_service = external_service or ExternalIntegrationService()

    async def generate_client_alerts(self, client_id: Optional[int] = None) -> List[FinancialAlert]:
        """
        Genera alertas financieras para uno o todos los clientes.
        
        Args:
            client_id (Optional[int]): ID del cliente específico. 
                Si es None, genera alertas para todos los clientes.
        
        Returns:
            List[FinancialAlert]: Lista de alertas generadas
        """
        if client_id:
            return await self._generate_alerts_for_client(client_id)
        else:
            clients = self.db.query(Cliente).all()
            all_alerts = []
            for client in clients:
                client_alerts = await self._generate_alerts_for_client(client.id)
                all_alerts.extend(client_alerts)
            return all_alerts

    async def _generate_alerts_for_client(self, client_id: int) -> List[FinancialAlert]:
        """
        Genera alertas para un cliente específico.
        
        Args:
            client_id (int): ID del cliente
        
        Returns:
            List[FinancialAlert]: Lista de alertas generadas para el cliente
        """
        alerts = []
        
        # Alertas de riesgo de ingresos
        revenue_alerts = await self._check_revenue_risk(client_id)
        alerts.extend(revenue_alerts)
        
        # Alertas de flujo de efectivo
        cash_flow_alerts = await self._check_cash_flow_risk(client_id)
        alerts.extend(cash_flow_alerts)
        
        # Alertas de riesgo de crédito
        credit_risk_alerts = await self._check_credit_risk(client_id)
        alerts.extend(credit_risk_alerts)
        
        # Alertas de tendencias de mercado
        market_alerts = await self._check_market_trends(client_id)
        alerts.extend(market_alerts)
        
        return alerts

    async def _check_revenue_risk(self, client_id: int) -> List[FinancialAlert]:
        """
        Verifica riesgos relacionados con los ingresos del cliente.
        
        Args:
            client_id (int): ID del cliente
        
        Returns:
            List[FinancialAlert]: Alertas de riesgo de ingresos
        """
        alerts = []
        
        # Obtener facturas del cliente
        invoices = self.db.query(Factura).filter(
            Factura.cliente_id == client_id
        ).order_by(desc(Factura.fecha_expedicion)).limit(12).all()
        
        if not invoices:
            return alerts
        
        # Calcular tendencia de ingresos
        revenues = [invoice.total_factura for invoice in invoices]
        avg_revenue = sum(revenues) / len(revenues)
        last_revenue = revenues[0]
        
        # Alerta si los ingresos han disminuido significativamente
        if last_revenue < avg_revenue * 0.6:
            alert = FinancialAlert.create_alert(
                client_id=client_id,
                type=AlertType.REVENUE_RISK,
                severity=AlertSeverity.HIGH,
                title="Disminución Significativa de Ingresos",
                description=f"Los ingresos han caído por debajo del 60% del promedio. Último ingreso: {last_revenue}, Promedio: {avg_revenue}",
                current_value=last_revenue,
                threshold_value=avg_revenue * 0.6
            )
            alerts.append(alert)
        
        return alerts

    async def _check_cash_flow_risk(self, client_id: int) -> List[FinancialAlert]:
        """
        Verifica riesgos de flujo de efectivo.
        
        Args:
            client_id (int): ID del cliente
        
        Returns:
            List[FinancialAlert]: Alertas de flujo de efectivo
        """
        alerts = []
        
        # Obtener facturas pendientes de pago
        pending_invoices = self.db.query(Factura).filter(
            Factura.cliente_id == client_id,
            Factura.estado_pago != 'PAGADA'
        ).all()
        
        total_pending = sum(invoice.total_factura for invoice in pending_invoices)
        
        if total_pending > 10000:  # Umbral configurable
            alert = FinancialAlert.create_alert(
                client_id=client_id,
                type=AlertType.CASH_FLOW,
                severity=AlertSeverity.MEDIUM,
                title="Alto Volumen de Facturas Pendientes",
                description=f"Tienes {len(pending_invoices)} facturas pendientes por un total de {total_pending}",
                current_value=total_pending,
                threshold_value=10000
            )
            alerts.append(alert)
        
        return alerts

    async def _check_credit_risk(self, client_id: int) -> List[FinancialAlert]:
        """
        Verifica riesgos de crédito del cliente.
        
        Args:
            client_id (int): ID del cliente
        
        Returns:
            List[FinancialAlert]: Alertas de riesgo de crédito
        """
        alerts = []
        
        try:
            # Obtener puntuación de riesgo de crédito
            credit_score = await self.external_service.get_credit_risk_score(client_id)
            
            if credit_score < 500:  # Umbral de riesgo bajo
                alert = FinancialAlert.create_alert(
                    client_id=client_id,
                    type=AlertType.CREDIT_RISK,
                    severity=AlertSeverity.HIGH,
                    title="Riesgo de Crédito Alto",
                    description=f"Puntuación de riesgo de crédito muy baja: {credit_score}",
                    current_value=credit_score,
                    threshold_value=500
                )
                alerts.append(alert)
        
        except Exception as e:
            # Manejar errores en obtención de score de crédito
            alert = FinancialAlert.create_alert(
                client_id=client_id,
                type=AlertType.CREDIT_RISK,
                severity=AlertSeverity.LOW,
                title="Error en Evaluación de Riesgo",
                description=f"No se pudo obtener puntuación de riesgo: {str(e)}"
            )
            alerts.append(alert)
        
        return alerts

    async def _check_market_trends(self, client_id: int) -> List[FinancialAlert]:
        """
        Verifica tendencias de mercado que puedan afectar al cliente.
        
        Args:
            client_id (int): ID del cliente
        
        Returns:
            List[FinancialAlert]: Alertas de tendencias de mercado
        """
        alerts = []
        
        try:
            # Obtener indicadores económicos
            economic_indicators = await self.external_service.get_economic_indicators()
            
            inflation = economic_indicators.get('INFLATION', 0)
            
            if inflation > 5:  # Umbral de inflación alto
                alert = FinancialAlert.create_alert(
                    client_id=client_id,
                    type=AlertType.MARKET_TREND,
                    severity=AlertSeverity.MEDIUM,
                    title="Alta Inflación - Impacto Potencial",
                    description=f"Inflación actual: {inflation}%. Posible impacto en costos y márgenes.",
                    current_value=inflation,
                    threshold_value=5
                )
                alerts.append(alert)
        
        except Exception as e:
            # Manejar errores en obtención de indicadores
            alert = FinancialAlert.create_alert(
                client_id=client_id,
                type=AlertType.MARKET_TREND,
                severity=AlertSeverity.LOW,
                title="Error en Análisis de Tendencias",
                description=f"No se pudieron obtener indicadores económicos: {str(e)}"
            )
            alerts.append(alert)
        
        return alerts

    def save_alerts(self, alerts: List[FinancialAlert]):
        """
        Guarda las alertas generadas en la base de datos.
        
        Args:
            alerts (List[FinancialAlert]): Lista de alertas a guardar
        """
        for alert in alerts:
            self.db.add(alert)
        
        self.db.commit()

    async def get_active_alerts(
        self, 
        client_id: Optional[int] = None, 
        severity: Optional[AlertSeverity] = None
    ) -> List[FinancialAlert]:
        """
        Obtiene alertas activas con filtros opcionales.
        
        Args:
            client_id (Optional[int]): Filtrar por cliente
            severity (Optional[AlertSeverity]): Filtrar por severidad
        
        Returns:
            List[FinancialAlert]: Lista de alertas activas
        """
        query = self.db.query(FinancialAlert).filter(
            FinancialAlert.is_active == True
        )
        
        if client_id:
            query = query.filter(FinancialAlert.client_id == client_id)
        
        if severity:
            query = query.filter(FinancialAlert.severity == severity)
        
        return query.all()
