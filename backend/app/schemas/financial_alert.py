from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.financial_alert import AlertType, AlertSeverity

class FinancialAlertResponse(BaseModel):
    """
    Esquema de respuesta para alertas financieras.
    
    Proporciona una representación serializable de una alerta financiera
    para ser enviada a través de la API.
    """
    id: int
    client_id: int
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    
    metadata: Optional[Dict[str, Any]] = None
    
    is_active: bool
    is_resolved: bool
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        """Configuración para permitir la conversión desde ORM"""
        orm_mode = True
        use_enum_values = True
