from fastapi import APIRouter, HTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from typing import Dict

from ..monitoring.metrics import AEATMetrics

router = APIRouter()
metrics = AEATMetrics()

@router.get("/health")
async def health_check() -> Dict:
    """
    Endpoint para verificar la salud del sistema.
    Retorna información detallada sobre el estado de los servicios AEAT.
    """
    try:
        health_info = metrics.get_service_health()
        
        # Verificar si algún servicio está caído
        all_services_up = all(
            info['status'] == 'up'
            for info in health_info.values()
        )
        
        response = {
            'status': 'healthy' if all_services_up else 'degraded',
            'services': health_info
        }
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el estado de salud: {str(e)}"
        )

@router.get("/metrics")
async def get_metrics():
    """
    Endpoint para exponer métricas en formato Prometheus.
    """
    try:
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar métricas: {str(e)}"
        )

@router.get("/metrics/json")
async def get_metrics_json() -> Dict:
    """
    Endpoint para obtener métricas en formato JSON.
    Útil para integraciones que prefieren JSON sobre el formato Prometheus.
    """
    try:
        return metrics.export_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar métricas: {str(e)}"
        )
