from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base
from app.models.financial_alert import AlertType, AlertSeverity

class NotificationChannel(enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH_NOTIFICATION = "PUSH_NOTIFICATION"
    WEBHOOK = "WEBHOOK"

class AlertSubscription(Base):
    """
    Modelo de suscripción de alertas para configuración personalizada.
    
    Permite a los usuarios configurar:
    - Tipos de alertas a recibir
    - Canales de notificación
    - Umbrales de severidad
    """
    __tablename__ = 'alert_subscriptions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Tipos de alertas suscritos
    subscribed_alert_types = Column(String, nullable=False)  # Stored as comma-separated values
    
    # Canales de notificación
    notification_channels = Column(String, nullable=False)  # Stored as comma-separated values
    
    # Configuración de severidad
    min_severity = Column(Enum(AlertSeverity), default=AlertSeverity.LOW)
    
    # Configuraciones adicionales
    is_active = Column(Boolean, default=True)
    
    # Metadatos de configuración
    webhook_url = Column(String, nullable=True)
    email_address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="alert_subscriptions")

    def set_alert_types(self, alert_types: list[AlertType]):
        """
        Establecer tipos de alerta suscritos.
        
        Args:
            alert_types (list[AlertType]): Lista de tipos de alerta
        """
        self.subscribed_alert_types = ','.join(
            alert_type.value for alert_type in alert_types
        )

    def get_alert_types(self) -> list[AlertType]:
        """
        Obtener tipos de alerta suscritos.
        
        Returns:
            list[AlertType]: Lista de tipos de alerta
        """
        return [
            AlertType(alert_type) 
            for alert_type in self.subscribed_alert_types.split(',') 
            if alert_type
        ]

    def set_notification_channels(self, channels: list[NotificationChannel]):
        """
        Establecer canales de notificación.
        
        Args:
            channels (list[NotificationChannel]): Lista de canales
        """
        self.notification_channels = ','.join(
            channel.value for channel in channels
        )

    def get_notification_channels(self) -> list[NotificationChannel]:
        """
        Obtener canales de notificación.
        
        Returns:
            list[NotificationChannel]: Lista de canales
        """
        return [
            NotificationChannel(channel) 
            for channel in self.notification_channels.split(',') 
            if channel
        ]

    @classmethod
    def create_subscription(
        cls,
        user_id: int,
        alert_types: list[AlertType],
        notification_channels: list[NotificationChannel],
        min_severity: AlertSeverity = AlertSeverity.LOW,
        webhook_url: str = None,
        email_address: str = None,
        phone_number: str = None
    ):
        """
        Método de fábrica para crear suscripciones de manera consistente.
        
        Args:
            user_id (int): ID del usuario
            alert_types (list[AlertType]): Tipos de alerta
            notification_channels (list[NotificationChannel]): Canales de notificación
            min_severity (AlertSeverity, optional): Severidad mínima. Defaults to LOW.
            webhook_url (str, optional): URL de webhook
            email_address (str, optional): Dirección de email
            phone_number (str, optional): Número de teléfono
        
        Returns:
            AlertSubscription: Nueva suscripción de alerta
        """
        subscription = cls(
            user_id=user_id,
            min_severity=min_severity,
            webhook_url=webhook_url,
            email_address=email_address,
            phone_number=phone_number
        )
        
        subscription.set_alert_types(alert_types)
        subscription.set_notification_channels(notification_channels)
        
        return subscription
