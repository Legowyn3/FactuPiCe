from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.models.alert_configuration import AlertConfiguration
from app.core.database import Base
from app.core.notification_manager import NotificationChannel

class AlertConfigurationService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert_configuration(
        self, 
        user_id: int, 
        alert_type: str, 
        threshold: Dict[str, Any], 
        notification_channels: List[NotificationChannel] = None,
        recipients: Optional[List[str]] = None
    ) -> AlertConfiguration:
        """
        Crear una nueva configuración de alerta personalizada.
        
        Args:
            user_id (int): ID del usuario
            alert_type (str): Tipo de alerta
            threshold (Dict): Umbrales de la alerta
            notification_channels (List[NotificationChannel]): Canales de notificación
            recipients (Optional[List[str]]): Destinatarios personalizados
        
        Returns:
            AlertConfiguration: Configuración de alerta creada
        """
        # Validar que el usuario exista
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")

        # Crear configuración de alerta
        alert_config = AlertConfiguration(
            user_id=user_id,
            alert_type=alert_type,
            threshold=threshold,
            notification_channels=notification_channels or [NotificationChannel.EMAIL],
            recipients=recipients or []
        )

        self.db.add(alert_config)
        self.db.commit()
        self.db.refresh(alert_config)

        return alert_config

    def update_alert_configuration(
        self, 
        configuration_id: int, 
        updates: Dict[str, Any]
    ) -> AlertConfiguration:
        """
        Actualizar una configuración de alerta existente.
        
        Args:
            configuration_id (int): ID de la configuración
            updates (Dict): Campos a actualizar
        
        Returns:
            AlertConfiguration: Configuración de alerta actualizada
        """
        alert_config = self.db.query(AlertConfiguration).filter(
            AlertConfiguration.id == configuration_id
        ).first()

        if not alert_config:
            raise ValueError(f"Configuración de alerta con ID {configuration_id} no encontrada")

        # Actualizar campos permitidos
        for key, value in updates.items():
            if hasattr(alert_config, key):
                setattr(alert_config, key, value)

        self.db.commit()
        self.db.refresh(alert_config)

        return alert_config

    def get_user_alert_configurations(
        self, 
        user_id: int, 
        alert_type: Optional[str] = None
    ) -> List[AlertConfiguration]:
        """
        Obtener configuraciones de alerta de un usuario.
        
        Args:
            user_id (int): ID del usuario
            alert_type (Optional[str]): Filtrar por tipo de alerta
        
        Returns:
            List[AlertConfiguration]: Configuraciones de alerta
        """
        query = self.db.query(AlertConfiguration).filter(
            AlertConfiguration.user_id == user_id
        )

        if alert_type:
            query = query.filter(AlertConfiguration.alert_type == alert_type)

        return query.all()

    def delete_alert_configuration(self, configuration_id: int):
        """
        Eliminar una configuración de alerta.
        
        Args:
            configuration_id (int): ID de la configuración a eliminar
        """
        alert_config = self.db.query(AlertConfiguration).filter(
            AlertConfiguration.id == configuration_id
        ).first()

        if not alert_config:
            raise ValueError(f"Configuración de alerta con ID {configuration_id} no encontrada")

        self.db.delete(alert_config)
        self.db.commit()

    def validate_alert_threshold(
        self, 
        alert_type: str, 
        current_value: Any, 
        threshold: Dict[str, Any]
    ) -> bool:
        """
        Validar si un valor actual supera un umbral de alerta.
        
        Args:
            alert_type (str): Tipo de alerta
            current_value (Any): Valor actual
            threshold (Dict): Configuración de umbral
        
        Returns:
            bool: True si se supera el umbral, False en caso contrario
        """
        try:
            if alert_type == 'REVENUE_DROP':
                # Ejemplo de validación de caída de ingresos
                return (
                    current_value <= threshold.get('max_value', float('inf')) and
                    current_value >= threshold.get('min_value', float('-inf'))
                )
            
            elif alert_type == 'CLIENT_CONCENTRATION':
                # Ejemplo de validación de concentración de clientes
                return current_value > threshold.get('max_percentage', 100)
            
            elif alert_type == 'INVOICE_OVERDUE':
                # Ejemplo de validación de facturas pendientes
                return current_value > threshold.get('max_days', 30)
            
            else:
                # Tipo de alerta no reconocido
                return False
        
        except Exception as e:
            # Manejar errores de validación
            print(f"Error en validación de umbral: {e}")
            return False

    def get_recommended_thresholds(self, alert_type: str) -> Dict[str, Any]:
        """
        Obtener umbrales recomendados para un tipo de alerta.
        
        Args:
            alert_type (str): Tipo de alerta
        
        Returns:
            Dict: Umbrales recomendados
        """
        recommended_thresholds = {
            'REVENUE_DROP': {
                'description': 'Alerta de caída significativa de ingresos',
                'default_threshold': {
                    'min_value': 0,
                    'max_value': 5000,  # Ejemplo de umbral
                    'percentage_drop': 20
                }
            },
            'CLIENT_CONCENTRATION': {
                'description': 'Alerta de alta concentración de clientes',
                'default_threshold': {
                    'max_percentage': 50,  # Máximo porcentaje de ingresos de un cliente
                    'max_clients': 3  # Máximo número de clientes que concentran ingresos
                }
            },
            'INVOICE_OVERDUE': {
                'description': 'Alerta de facturas pendientes',
                'default_threshold': {
                    'max_days': 30,  # Máximo días de factura pendiente
                    'max_amount': 10000  # Máximo importe de facturas pendientes
                }
            },
            'HIGH_REVENUE_VOLATILITY': {
                'description': 'Alerta de alta volatilidad de ingresos',
                'default_threshold': {
                    'max_coefficient_of_variation': 0.5
                }
            }
        }

        return recommended_thresholds.get(alert_type, {})

    def suggest_notification_channels(self, alert_type: str) -> List[NotificationChannel]:
        """
        Sugerir canales de notificación según el tipo de alerta.
        
        Args:
            alert_type (str): Tipo de alerta
        
        Returns:
            List[NotificationChannel]: Canales de notificación sugeridos
        """
        channel_suggestions = {
            'REVENUE_DROP': [
                NotificationChannel.EMAIL, 
                NotificationChannel.PUSH
            ],
            'CLIENT_CONCENTRATION': [
                NotificationChannel.EMAIL, 
                NotificationChannel.SMS
            ],
            'INVOICE_OVERDUE': [
                NotificationChannel.EMAIL, 
                NotificationChannel.SMS, 
                NotificationChannel.WEBHOOK
            ],
            'HIGH_REVENUE_VOLATILITY': [
                NotificationChannel.EMAIL, 
                NotificationChannel.PUSH
            ]
        }

        return channel_suggestions.get(alert_type, [NotificationChannel.EMAIL])
