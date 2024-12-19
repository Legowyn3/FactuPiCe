from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.financial_alert_service import FinancialAlertService
from app.models.financial_alert import FinancialAlert, AlertSeverity
from app.schemas.financial_alert import FinancialAlertResponse

router = APIRouter(
    prefix="/financial-alerts",
    tags=["Financial Alerts"]
)

@router.get("/", response_model=List[FinancialAlertResponse])
async def get_financial_alerts(
    db: Session = Depends(get_db),
    client_id: Optional[int] = None,
    severity: Optional[AlertSeverity] = None
):
    """
    Obtener alertas financieras con filtros opcionales.
    
    - Si no se especifica client_id, se obtienen alertas de todos los clientes
    - Si no se especifica severity, se obtienen todas las severidades
    """
    alert_service = FinancialAlertService(db)
    
    try:
        alerts = await alert_service.get_active_alerts(
            client_id=client_id, 
            severity=severity
        )
        return [
            FinancialAlertResponse.from_orm(alert) 
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_financial_alerts(
    client_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Generar alertas financieras para uno o todos los clientes.
    
    - Si no se especifica client_id, genera alertas para todos los clientes
    """
    alert_service = FinancialAlertService(db)
    
    try:
        alerts = await alert_service.generate_client_alerts(client_id)
        alert_service.save_alerts(alerts)
        
        return {
            "message": f"Generadas {len(alerts)} alertas",
            "alerts": [alert.id for alert in alerts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
