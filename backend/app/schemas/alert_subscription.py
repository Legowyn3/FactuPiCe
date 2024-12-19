from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

from app.models.financial_alert import AlertType, AlertSeverity
from app.models.alert_subscription import NotificationChannel

class AlertSubscriptionCreate(BaseModel):
    """
    Esquema para crear o actualizar una suscripción de alerta.
    
    Validaciones:
    - Al menos un tipo de alerta
    - Al menos un canal de notificación
    """
    user_id: int
    alert_types: List[AlertType]
    notification_channels: List[NotificationChannel]
    min_severity: Optional[AlertSeverity] = AlertSeverity.LOW
    
    webhook_url: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    
    @validator('alert_types')
    def validate_alert_types(cls, v):
        """Validar que se proporcione al menos un tipo de alerta"""
        if not v:
            raise ValueError("Debe especificar al menos un tipo de alerta")
        return v
    
    @validator('notification_channels')
    def validate_notification_channels(cls, v):
        """Validar que se proporcione al menos un canal de notificación"""
        if not v:
            raise ValueError("Debe especificar al menos un canal de notificación")
        return v

class AlertSubscriptionResponse(BaseModel):
    """
    Esquema de respuesta para suscripciones de alerta.
    
    Proporciona una representación serializable de una suscripción.
    """
    id: int
    user_id: int
    subscribed_alert_types: str
    notification_channels: str
    min_severity: AlertSeverity
    
    webhook_url: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    
    is_active: bool
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        """Configuración para permitir la conversión desde ORM"""
        orm_mode = True
        use_enum_values = True
    
    def get_alert_types(self) -> List[AlertType]:
        """
        Convertir tipos de alerta de cadena a lista de enums.
        
        Returns:
            List[AlertType]: Lista de tipos de alerta
        """
        return [
            AlertType(alert_type) 
            for alert_type in self.subscribed_alert_types.split(',') 
            if alert_type
        ]
    
    def get_notification_channels(self) -> List[NotificationChannel]:
        """
        Convertir canales de notificación de cadena a lista de enums.
        
        Returns:
            List[NotificationChannel]: Lista de canales de notificación
        """
        return [
            NotificationChannel(channel) 
            for channel in self.notification_channels.split(',') 
            if channel
        ]
