import xml.etree.ElementTree as ET
import uuid
from datetime import datetime, timedelta
import pytz
from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.factura import Factura
from ..models.cliente import Cliente
from ..utils.facturae import FacturaEGenerator
from ..schemas.factura import FacturaCreate, TipoFactura, EstadoFactura

class FacturaEService:
    def __init__(self):
        self.generator = FacturaEGenerator()
        self.timezone = pytz.timezone('Europe/Madrid')

    async def generate_facturae(self, db: Session, factura: Factura) -> Dict[str, Any]:
        """
        Genera todos los elementos necesarios para una factura electrónica válida.
        
        Soporta diferentes tipos de facturas:
        - Factura normal
        - Factura rectificativa
        - Factura simplificada
        - Factura recapitulativa
        """
        try:
            # Obtener información del cliente
            cliente = db.query(Cliente).filter(Cliente.id == factura.cliente_id).first()
            if not cliente:
                raise ValueError("Cliente no encontrado")

            # Información del software
            software_info = {
                'name': 'AspiMur',
                'version': '1.0.0',
                'license': 'Comercial'
            }

            # Validaciones previas a la generación
            validation_result = await self.validate_facturae(factura)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }

            # Lógica especial según el tipo de factura
            if factura.tipo == TipoFactura.rectificativa:
                # Validar factura original para rectificativas
                factura_original = db.query(Factura).filter(
                    Factura.id == factura.factura_original_id
                ).first()
                if not factura_original:
                    raise ValueError("Factura original no encontrada para factura rectificativa")

            # Generar XML base
            xml_root = self.generator.generate_xml(factura, cliente, software_info)
            xml_content = ET.tostring(xml_root, encoding='UTF-8', xml_declaration=True)

            # Generar identificadores únicos
            factura.invoice_hash = self._generate_invoice_hash(factura)
            factura.tbai_identifier = self._generate_tbai_id(factura)
            
            # Generar código QR
            factura.qr_code = self.generator.generate_qr(factura)

            # Preparar datos de retorno
            return {
                'success': True,
                'xml_content': xml_content,
                'invoice_hash': factura.invoice_hash,
                'tbai_identifier': factura.tbai_identifier,
                'qr_code': factura.qr_code
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def validate_facturae(self, factura: Factura) -> Dict[str, Any]:
        """
        Validación avanzada de facturas con reglas específicas según su tipo.
        """
        validation_results = {
            'is_valid': True,
            'errors': []
        }

        # Validaciones comunes
        validation_results = self._validate_common_fields(factura, validation_results)

        # Validaciones específicas según el tipo de factura
        if factura.tipo == TipoFactura.normal:
            validation_results = self._validate_normal_invoice(factura, validation_results)
        elif factura.tipo == TipoFactura.rectificativa:
            validation_results = self._validate_rectificativa_invoice(factura, validation_results)
        elif factura.tipo == TipoFactura.simplificada:
            validation_results = self._validate_simplificada_invoice(factura, validation_results)
        elif factura.tipo == TipoFactura.recapitulativa:
            validation_results = self._validate_recapitulativa_invoice(factura, validation_results)

        # Validaciones finales de importes
        validation_results = self._validate_invoice_amounts(factura, validation_results)

        return validation_results

    def _validate_common_fields(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones comunes para todos los tipos de facturas."""
        required_fields = [
            ('serie', factura.serie),
            ('numero', factura.numero),
            ('fecha_expedicion', factura.fecha_expedicion),
            ('cliente_id', factura.cliente_id),
            ('base_imponible', factura.base_imponible),
            ('tipo_iva', factura.tipo_iva),
            ('total_factura', factura.total_factura)
        ]

        for field_name, field_value in required_fields:
            if not field_value:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Campo requerido '{field_name}' no puede estar vacío")

        # Validar rango de fechas
        if factura.fecha_expedicion:
            max_past_date = datetime.now(self.timezone) - timedelta(days=365 * 5)
            max_future_date = datetime.now(self.timezone) + timedelta(days=30)
            
            if factura.fecha_expedicion < max_past_date or factura.fecha_expedicion > max_future_date:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Fecha de expedición fuera de rango válido")

        return validation_results

    def _validate_normal_invoice(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones específicas para facturas normales."""
        # Validar que la base imponible sea positiva
        if factura.base_imponible <= 0:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Base imponible debe ser positiva en facturas normales")

        return validation_results

    def _validate_rectificativa_invoice(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones específicas para facturas rectificativas."""
        # Validar que exista factura original
        if not factura.factura_original_id:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Factura rectificativa requiere referencia a factura original")

        # Permitir base imponible negativa
        if not factura.motivo_rectificacion:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Factura rectificativa requiere motivo de rectificación")

        return validation_results

    def _validate_simplificada_invoice(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones específicas para facturas simplificadas."""
        # Límite de importe para facturas simplificadas
        LIMITE_FACTURA_SIMPLIFICADA = 3000  # Límite según normativa española

        if factura.total_factura > LIMITE_FACTURA_SIMPLIFICADA:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Importe excede límite para factura simplificada ({LIMITE_FACTURA_SIMPLIFICADA}€)")

        return validation_results

    def _validate_recapitulativa_invoice(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones específicas para facturas recapitulativas."""
        if not factura.periodo_recapitulativo:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Factura recapitulativa requiere periodo")

        return validation_results

    def _validate_invoice_amounts(self, factura: Factura, validation_results: Dict) -> Dict:
        """Validaciones finales de importes."""
        try:
            # Calcular cuota de IVA
            expected_iva = round(factura.base_imponible * (factura.tipo_iva / 100), 2)
            if abs(expected_iva - factura.cuota_iva) > 0.01:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Cálculo de cuota de IVA incorrecto")

            # Calcular total esperado
            total_expected = factura.base_imponible + factura.cuota_iva

            # Considerar retención si existe
            if factura.tipo_retencion:
                retencion = round(factura.base_imponible * (factura.tipo_retencion / 100), 2)
                total_expected -= retencion

            # Validar total de factura
            if abs(total_expected - factura.total_factura) > 0.01:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Cálculo de total de factura incorrecto")

        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Error en validación de importes: {str(e)}")

        return validation_results

    def _generate_invoice_hash(self, factura: Factura) -> str:
        """
        Genera un hash único para la factura basado en sus datos.
        Incluye más campos para mayor unicidad.
        """
        hash_data = (
            f"{factura.serie}{factura.numero}"
            f"{factura.fecha_expedicion}"
            f"{factura.base_imponible}"
            f"{factura.total_factura}"
            f"{factura.cliente_id}"
            f"{factura.tipo}"
        )
        
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, hash_data))

    def _generate_tbai_id(self, factura: Factura) -> str:
        """
        Genera un identificador TicketBAI más completo.
        """
        # Formato: TBAI-[AÑO]-[SERIE]-[NÚMERO]-[TIPO]
        return f"TBAI-{factura.fecha_expedicion.year}-{factura.serie}-{factura.numero}-{factura.tipo.value}"

    async def get_invoice_history(self, db: Session, factura_id: int) -> List[Dict]:
        """
        Obtiene el historial de cambios de una factura.
        
        Args:
            db (Session): Sesión de base de datos
            factura_id (int): ID de la factura
        
        Returns:
            Lista de cambios históricos de la factura
        """
        from ..models.audit_log import AuditLog  # Importación local para evitar dependencias circulares

        # Buscar la factura original
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise ValueError(f"Factura con ID {factura_id} no encontrada")

        # Buscar logs de auditoría relacionados con esta factura
        audit_logs = db.query(AuditLog).filter(
            AuditLog.resource_type == 'Factura',
            AuditLog.resource_id == factura_id
        ).order_by(AuditLog.timestamp.desc()).all()

        # Transformar logs de auditoría
        history = []
        for log in audit_logs:
            history.append({
                'timestamp': log.timestamp,
                'user_id': log.user_id,
                'action': log.action,
                'changes': log.changes,
                'ip_address': log.ip_address
            })

        return history

    async def generate_invoice_report(self, db: Session, filters: Dict[str, Any]) -> Dict:
        """
        Genera un informe detallado de facturas con agregaciones y múltiples filtros.
        
        Args:
            db (Session): Sesión de base de datos
            filters (Dict[str, Any]): Diccionario de filtros para el informe
        
        Returns:
            Dict con métricas detalladas de facturas
        """
        from sqlalchemy import func, and_

        # Consulta base con múltiples agregaciones
        query = db.query(
            func.count(Factura.id).label('total_facturas'),
            func.sum(Factura.base_imponible).label('base_imponible_total'),
            func.sum(Factura.cuota_iva).label('total_iva'),
            func.sum(Factura.total_factura).label('total_facturado'),
            func.avg(Factura.total_factura).label('factura_media')
        )

        # Aplicar filtros dinámicamente
        conditions = []

        # Filtro por rango de fechas
        if filters.get('fecha_inicio'):
            conditions.append(Factura.fecha_expedicion >= filters['fecha_inicio'])
        if filters.get('fecha_fin'):
            conditions.append(Factura.fecha_expedicion <= filters['fecha_fin'])

        # Filtro por tipo de factura
        if filters.get('tipo'):
            conditions.append(Factura.tipo == filters['tipo'])

        # Filtro por cliente
        if filters.get('cliente_id'):
            conditions.append(Factura.cliente_id == filters['cliente_id'])

        # Filtro por rango de importes
        if filters.get('importe_minimo'):
            conditions.append(Factura.total_factura >= filters['importe_minimo'])
        if filters.get('importe_maximo'):
            conditions.append(Factura.total_factura <= filters['importe_maximo'])

        # Filtro por estado
        if filters.get('estado'):
            conditions.append(Factura.estado == filters['estado'])

        # Aplicar condiciones
        if conditions:
            query = query.filter(and_(*conditions))

        # Agrupar resultados si se solicita
        group_by = filters.get('group_by')
        if group_by:
            if group_by == 'tipo':
                query = query.group_by(Factura.tipo)
            elif group_by == 'cliente':
                query = query.group_by(Factura.cliente_id)
            elif group_by == 'mes':
                query = query.group_by(func.extract('month', Factura.fecha_expedicion))

        # Ejecutar consulta
        result = query.one()

        # Preparar informe detallado
        report = {
            'total_facturas': result.total_facturas,
            'base_imponible_total': result.base_imponible_total,
            'total_iva': result.total_iva,
            'total_facturado': result.total_facturado,
            'factura_media': result.factura_media,
            
            # Métricas adicionales
            'facturas_por_tipo': self._count_invoices_by_type(db, filters) if filters.get('group_by') == 'tipo' else None,
            'facturas_por_cliente': self._count_invoices_by_client(db, filters) if filters.get('group_by') == 'cliente' else None,
            'facturas_por_mes': self._count_invoices_by_month(db, filters) if filters.get('group_by') == 'mes' else None
        }

        return report

    def _count_invoices_by_type(self, db: Session, filters: Dict[str, Any]) -> Dict[str, int]:
        """Contar facturas por tipo."""
        from sqlalchemy import func
        
        query = db.query(
            Factura.tipo, 
            func.count(Factura.id).label('count')
        ).group_by(Factura.tipo)

        # Aplicar filtros comunes
        conditions = []
        if filters.get('fecha_inicio'):
            conditions.append(Factura.fecha_expedicion >= filters['fecha_inicio'])
        if filters.get('fecha_fin'):
            conditions.append(Factura.fecha_expedicion <= filters['fecha_fin'])
        
        if conditions:
            query = query.filter(and_(*conditions))

        return {str(row.tipo): row.count for row in query.all()}

    def _count_invoices_by_client(self, db: Session, filters: Dict[str, Any]) -> Dict[str, int]:
        """Contar facturas por cliente."""
        from sqlalchemy import func
        
        query = db.query(
            Factura.cliente_id, 
            func.count(Factura.id).label('count')
        ).group_by(Factura.cliente_id)

        # Aplicar filtros comunes
        conditions = []
        if filters.get('fecha_inicio'):
            conditions.append(Factura.fecha_expedicion >= filters['fecha_inicio'])
        if filters.get('fecha_fin'):
            conditions.append(Factura.fecha_expedicion <= filters['fecha_fin'])
        
        if conditions:
            query = query.filter(and_(*conditions))

        return {str(row.cliente_id): row.count for row in query.all()}

    def _count_invoices_by_month(self, db: Session, filters: Dict[str, Any]) -> Dict[str, int]:
        """Contar facturas por mes."""
        from sqlalchemy import func
        
        query = db.query(
            func.extract('month', Factura.fecha_expedicion).label('month'), 
            func.count(Factura.id).label('count')
        ).group_by('month')

        # Aplicar filtros comunes
        conditions = []
        if filters.get('fecha_inicio'):
            conditions.append(Factura.fecha_expedicion >= filters['fecha_inicio'])
        if filters.get('fecha_fin'):
            conditions.append(Factura.fecha_expedicion <= filters['fecha_fin'])
        
        if conditions:
            query = query.filter(and_(*conditions))

        return {str(int(row.month)): row.count for row in query.all()}
