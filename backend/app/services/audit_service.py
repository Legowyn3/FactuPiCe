from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.factura import Factura
from ..models.audit_log import AuditLog  # Necesitaremos crear este modelo

class AuditService:
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivos de registro separados por tipo
        self.files = {
            'security': self.log_dir / 'security.log',
            'ticketbai': self.log_dir / 'ticketbai.log',
            'invoice': self.log_dir / 'invoice.log',
            'error': self.log_dir / 'error.log'
        }

    async def log_invoice_operation(
        self,
        db: Session,
        operation: str,
        factura: Factura,
        result: Dict[str, Any],
        user_id: Optional[int] = None
    ):
        """Registra una operación relacionada con facturas."""
        timestamp = datetime.now()
        
        # Crear entrada en la base de datos
        audit_entry = AuditLog(
            timestamp=timestamp,
            operation_type=operation,
            entity_type='invoice',
            entity_id=factura.id,
            user_id=user_id,
            details=json.dumps({
                'invoice_number': factura.numero,
                'operation': operation,
                'result': result
            }),
            success=result.get('success', False)
        )
        
        db.add(audit_entry)
        db.commit()
        
        # Registrar en archivo de log
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'operation': operation,
            'invoice_id': factura.id,
            'invoice_number': factura.numero,
            'user_id': user_id,
            'result': result
        }
        
        self._write_log('invoice', log_entry)
        
        # Si hay error, registrar también en el log de errores
        if not result.get('success', False):
            self._write_log('error', log_entry)

    async def log_ticketbai_operation(
        self,
        operation: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any]
    ):
        """Registra una operación de TicketBAI."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'request': request_data,
            'response': response_data
        }
        
        self._write_log('ticketbai', log_entry)
        
        # Si hay error, registrar también en el log de errores
        if not response_data.get('success', False):
            self._write_log('error', log_entry)

    async def log_security_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None
    ):
        """Registra un evento de seguridad."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        self._write_log('security', log_entry)
        
        # Si es un evento de seguridad crítico, registrar también en errores
        if details.get('severity') == 'critical':
            self._write_log('error', log_entry)

    def _write_log(self, log_type: str, entry: Dict[str, Any]):
        """Escribe una entrada en el archivo de log correspondiente."""
        log_file = self.files.get(log_type)
        if log_file:
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')

    async def get_invoice_history(
        self,
        db: Session,
        factura_id: int
    ) -> list[AuditLog]:
        """Obtiene el historial de operaciones de una factura."""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == 'invoice',
            AuditLog.entity_id == factura_id
        ).order_by(AuditLog.timestamp.desc()).all()

    async def get_security_events(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        event_type: Optional[str] = None
    ) -> list[AuditLog]:
        """Obtiene eventos de seguridad en un rango de fechas."""
        query = db.query(AuditLog).filter(
            AuditLog.entity_type == 'security',
            AuditLog.timestamp.between(start_date, end_date)
        )
        
        if event_type:
            query = query.filter(AuditLog.operation_type == event_type)
        
        return query.order_by(AuditLog.timestamp.desc()).all()

    async def get_error_logs(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> list[Dict[str, Any]]:
        """Obtiene logs de error en un rango de fechas."""
        errors = []
        with open(self.files['error']) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry['timestamp'])
                    if start_date <= entry_date <= end_date:
                        errors.append(entry)
                except Exception:
                    continue
        return errors

    async def get_operation_statistics(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de operaciones en un rango de fechas."""
        stats = {
            'total_operations': 0,
            'success_rate': 0,
            'operations_by_type': {},
            'errors_by_type': {},
            'average_response_time': 0
        }
        
        # Consultar todas las operaciones en el rango
        operations = db.query(AuditLog).filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).all()
        
        total_time = 0
        success_count = 0
        
        for op in operations:
            stats['total_operations'] += 1
            
            # Conteo por tipo de operación
            op_type = op.operation_type
            stats['operations_by_type'][op_type] = \
                stats['operations_by_type'].get(op_type, 0) + 1
            
            # Conteo de éxitos
            if op.success:
                success_count += 1
            else:
                # Analizar errores
                try:
                    details = json.loads(op.details)
                    error_type = details.get('error', {}).get('type', 'unknown')
                    stats['errors_by_type'][error_type] = \
                        stats['errors_by_type'].get(error_type, 0) + 1
                except json.JSONDecodeError:
                    pass
            
            # Calcular tiempo de respuesta si está disponible
            try:
                details = json.loads(op.details)
                if 'response_time' in details:
                    total_time += details['response_time']
            except json.JSONDecodeError:
                pass
        
        # Calcular estadísticas finales
        if stats['total_operations'] > 0:
            stats['success_rate'] = (success_count / stats['total_operations']) * 100
            if total_time > 0:
                stats['average_response_time'] = \
                    total_time / stats['total_operations']
        
        return stats

    async def export_audit_data(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        format: str = 'json'
    ) -> str:
        """Exporta datos de auditoría en varios formatos."""
        # Obtener todas las entradas de auditoría en el rango
        entries = db.query(AuditLog).filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).order_by(AuditLog.timestamp).all()
        
        # Convertir a formato de exportación
        export_data = []
        for entry in entries:
            export_data.append({
                'timestamp': entry.timestamp.isoformat(),
                'operation_type': entry.operation_type,
                'entity_type': entry.entity_type,
                'entity_id': entry.entity_id,
                'user_id': entry.user_id,
                'details': json.loads(entry.details) if entry.details else {},
                'success': entry.success
            })
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['timestamp', 'operation_type', 'entity_type',
                           'entity_id', 'user_id', 'details', 'success']
            )
            
            writer.writeheader()
            for entry in export_data:
                entry['details'] = json.dumps(entry['details'])  # Convertir dict a string
                writer.writerow(entry)
            
            return output.getvalue()
        else:
            raise ValueError(f"Formato de exportación no soportado: {format}")

    async def cleanup_old_logs(
        self,
        db: Session,
        retention_days: int,
        backup_dir: Optional[str] = None
    ):
        """Limpia logs antiguos y opcionalmente los respalda."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Respaldar logs si se especifica un directorio
        if backup_dir:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Exportar logs antiguos
            old_logs = await self.export_audit_data(
                db,
                datetime.min,
                cutoff_date,
                format='json'
            )
            
            backup_file = backup_path / f"audit_backup_{cutoff_date.date()}.json"
            with open(backup_file, 'w') as f:
                f.write(old_logs)
        
        # Eliminar logs antiguos de la base de datos
        db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        # Limpiar archivos de log
        for log_file in self.files.values():
            if log_file.exists():
                # Crear archivo temporal con logs recientes
                temp_file = log_file.with_suffix('.tmp')
                with open(log_file) as old, open(temp_file, 'w') as new:
                    for line in old:
                        try:
                            entry = json.loads(line)
                            entry_date = datetime.fromisoformat(entry['timestamp'])
                            if entry_date >= cutoff_date:
                                new.write(line)
                        except Exception:
                            continue
                
                # Reemplazar archivo original
                temp_file.replace(log_file)
