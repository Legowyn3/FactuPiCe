from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge
import logging

# Métricas de Prometheus
AEAT_REQUEST_COUNT = Counter(
    'aeat_request_total',
    'Total de peticiones a la AEAT',
    ['operation', 'status']
)

AEAT_REQUEST_DURATION = Histogram(
    'aeat_request_duration_seconds',
    'Duración de las peticiones a la AEAT',
    ['operation']
)

AEAT_ERROR_COUNT = Counter(
    'aeat_error_total',
    'Total de errores en peticiones a la AEAT',
    ['operation', 'error_code']
)

AEAT_RETRY_COUNT = Counter(
    'aeat_retry_total',
    'Total de reintentos en peticiones a la AEAT',
    ['operation']
)

AEAT_SERVICE_STATUS = Gauge(
    'aeat_service_status',
    'Estado del servicio AEAT',
    ['service']
)

class AEATMetrics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._service_status = {}
        self._error_window = {}
        self._request_times = {}

    def record_request(
        self,
        operation: str,
        duration: float,
        status: str,
        error_code: Optional[str] = None
    ):
        """Registra una petición a la AEAT."""
        # Incrementar contador de peticiones
        AEAT_REQUEST_COUNT.labels(operation=operation, status=status).inc()
        
        # Registrar duración
        AEAT_REQUEST_DURATION.labels(operation=operation).observe(duration)
        
        # Si hay error, registrarlo
        if error_code:
            AEAT_ERROR_COUNT.labels(
                operation=operation,
                error_code=error_code
            ).inc()
        
        # Actualizar ventana de errores
        self._update_error_window(operation, error_code)
        
        # Actualizar tiempos de respuesta
        self._update_request_times(operation, duration)
        
        # Actualizar estado del servicio
        self._update_service_status(operation, status == 'success')

    def record_retry(self, operation: str):
        """Registra un reintento de operación."""
        AEAT_RETRY_COUNT.labels(operation=operation).inc()

    def _update_error_window(self, operation: str, error_code: Optional[str]):
        """Mantiene una ventana deslizante de errores."""
        now = datetime.now()
        window_size = timedelta(minutes=5)
        
        if operation not in self._error_window:
            self._error_window[operation] = []
        
        # Añadir nuevo error si existe
        if error_code:
            self._error_window[operation].append({
                'timestamp': now,
                'error_code': error_code
            })
        
        # Limpiar errores antiguos
        self._error_window[operation] = [
            error for error in self._error_window[operation]
            if now - error['timestamp'] <= window_size
        ]

    def _update_request_times(self, operation: str, duration: float):
        """Actualiza las estadísticas de tiempos de respuesta."""
        now = datetime.now()
        window_size = timedelta(minutes=5)
        
        if operation not in self._request_times:
            self._request_times[operation] = []
        
        self._request_times[operation].append({
            'timestamp': now,
            'duration': duration
        })
        
        # Limpiar tiempos antiguos
        self._request_times[operation] = [
            req for req in self._request_times[operation]
            if now - req['timestamp'] <= window_size
        ]

    def _update_service_status(self, operation: str, success: bool):
        """Actualiza el estado del servicio."""
        if operation not in self._service_status:
            self._service_status[operation] = {
                'status': 'up',
                'last_check': datetime.now(),
                'consecutive_failures': 0
            }
        
        status = self._service_status[operation]
        status['last_check'] = datetime.now()
        
        if success:
            status['consecutive_failures'] = 0
            status['status'] = 'up'
        else:
            status['consecutive_failures'] += 1
            if status['consecutive_failures'] >= 3:
                status['status'] = 'down'
        
        AEAT_SERVICE_STATUS.labels(service=operation).set(
            1 if status['status'] == 'up' else 0
        )

    def get_service_health(self) -> Dict:
        """Obtiene el estado de salud de los servicios."""
        health_info = {}
        
        for operation, status in self._service_status.items():
            # Calcular tasa de error
            error_rate = self._calculate_error_rate(operation)
            
            # Calcular estadísticas de tiempo de respuesta
            response_stats = self._calculate_response_stats(operation)
            
            health_info[operation] = {
                'status': status['status'],
                'last_check': status['last_check'].isoformat(),
                'error_rate': error_rate,
                'response_times': response_stats
            }
        
        return health_info

    def _calculate_error_rate(self, operation: str) -> float:
        """Calcula la tasa de error para una operación."""
        if operation not in self._error_window:
            return 0.0
        
        total_errors = len(self._error_window[operation])
        total_requests = len(self._request_times[operation])
        
        if total_requests == 0:
            return 0.0
        
        return (total_errors / total_requests) * 100

    def _calculate_response_stats(self, operation: str) -> Dict:
        """Calcula estadísticas de tiempos de respuesta."""
        if operation not in self._request_times or not self._request_times[operation]:
            return {
                'avg': 0,
                'p95': 0,
                'p99': 0,
                'max': 0
            }
        
        durations = [req['duration'] for req in self._request_times[operation]]
        durations.sort()
        
        return {
            'avg': sum(durations) / len(durations),
            'p95': durations[int(len(durations) * 0.95)],
            'p99': durations[int(len(durations) * 0.99)],
            'max': max(durations)
        }

    def export_metrics(self) -> str:
        """Exporta las métricas en formato JSON."""
        return json.dumps({
            'service_health': self.get_service_health(),
            'error_rates': {
                op: self._calculate_error_rate(op)
                for op in self._service_status.keys()
            },
            'response_times': {
                op: self._calculate_response_stats(op)
                for op in self._service_status.keys()
            }
        }, indent=2)
