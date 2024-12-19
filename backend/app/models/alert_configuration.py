from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import PickleType

from app.core.database import Base
from app.core.notification_manager import NotificationChannel

class AlertConfiguration(Base):
    """
    Modelo para configuraciones de alerta personalizadas.
    """
    __tablename__ = 'alert_configurations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    alert_type = Column(String, nullable=False)
    threshold = Column(JSON, nullable=False)
    notification_channels = Column(PickleType, nullable=True)
    recipients = Column(JSON, nullable=True)
    is_active = Column(Integer, default=1)
    
    # Relación con el usuario
    user = relationship("User", back_populates="alert_configurations")

    def __repr__(self):
        return f"<AlertConfiguration(id={self.id}, type={self.alert_type}, user_id={self.user_id})>"

    def to_dict(self):
        """
        Convertir configuración de alerta a diccionario.
        
        Returns:
            Dict: Representación en diccionario de la configuración
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'threshold': self.threshold,
            'notification_channels': [
                channel.name for channel in self.notification_channels
            ] if self.notification_channels else [],
            'recipients': self.recipients,
            'is_active': bool(self.is_active)
        }
