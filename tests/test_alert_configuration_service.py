import pytest
from sqlalchemy.orm import Session

from app.services.alert_configuration_service import AlertConfigurationService
from app.models.user import User
from app.core.database import SessionLocal
from app.core.notification_manager import NotificationChannel

@pytest.fixture
def db_session():
    """Crear una sesión de base de datos para pruebas"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def user(db_session):
    """Crear un usuario de prueba"""
    test_user = User(
        username="testuser", 
        email="test@example.com", 
        is_active=True
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    return test_user

@pytest.fixture
def alert_configuration_service(db_session):
    """Crear instancia del servicio de configuración de alertas"""
    return AlertConfigurationService(db_session)

def test_create_alert_configuration(alert_configuration_service, db_session, user):
    """Prueba creación de configuración de alerta"""
    # Configuración de alerta de ejemplo
    alert_config = alert_configuration_service.create_alert_configuration(
        user_id=user.id,
        alert_type='REVENUE_DROP',
        threshold={
            'min_value': 0,
            'max_value': 5000,
            'percentage_drop': 20
        },
        notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        recipients=['finance@company.com']
    )

    # Verificaciones
    assert alert_config.id is not None
    assert alert_config.user_id == user.id
    assert alert_config.alert_type == 'REVENUE_DROP'
    assert alert_config.threshold == {
        'min_value': 0,
        'max_value': 5000,
        'percentage_drop': 20
    }
    assert len(alert_config.notification_channels) == 2
    assert alert_config.recipients == ['finance@company.com']

def test_update_alert_configuration(alert_configuration_service, db_session, user):
    """Prueba actualización de configuración de alerta"""
    # Crear configuración inicial
    initial_config = alert_configuration_service.create_alert_configuration(
        user_id=user.id,
        alert_type='CLIENT_CONCENTRATION',
        threshold={'max_percentage': 50}
    )

    # Actualizar configuración
    updated_config = alert_configuration_service.update_alert_configuration(
        configuration_id=initial_config.id,
        updates={
            'threshold': {'max_percentage': 40},
            'notification_channels': [NotificationChannel.PUSH]
        }
    )

    # Verificaciones
    assert updated_config.id == initial_config.id
    assert updated_config.threshold == {'max_percentage': 40}
    assert len(updated_config.notification_channels) == 1
    assert updated_config.notification_channels[0] == NotificationChannel.PUSH

def test_get_user_alert_configurations(alert_configuration_service, db_session, user):
    """Prueba obtención de configuraciones de alerta de un usuario"""
    # Crear múltiples configuraciones
    alert_configuration_service.create_alert_configuration(
        user_id=user.id,
        alert_type='REVENUE_DROP',
        threshold={'percentage_drop': 20}
    )
    alert_configuration_service.create_alert_configuration(
        user_id=user.id,
        alert_type='INVOICE_OVERDUE',
        threshold={'max_days': 30}
    )

    # Obtener configuraciones
    all_configs = alert_configuration_service.get_user_alert_configurations(user.id)
    revenue_configs = alert_configuration_service.get_user_alert_configurations(
        user.id, 
        alert_type='REVENUE_DROP'
    )

    # Verificaciones
    assert len(all_configs) == 2
    assert len(revenue_configs) == 1
    assert revenue_configs[0].alert_type == 'REVENUE_DROP'

def test_delete_alert_configuration(alert_configuration_service, db_session, user):
    """Prueba eliminación de configuración de alerta"""
    # Crear configuración
    alert_config = alert_configuration_service.create_alert_configuration(
        user_id=user.id,
        alert_type='HIGH_REVENUE_VOLATILITY',
        threshold={'max_coefficient_of_variation': 0.5}
    )

    # Eliminar configuración
    alert_configuration_service.delete_alert_configuration(alert_config.id)

    # Verificar eliminación
    with pytest.raises(ValueError):
        alert_configuration_service.delete_alert_configuration(alert_config.id)

def test_validate_alert_threshold(alert_configuration_service):
    """Prueba validación de umbrales de alerta"""
    # Pruebas para diferentes tipos de alerta
    test_cases = [
        {
            'alert_type': 'REVENUE_DROP',
            'current_value': 3000,
            'threshold': {'min_value': 0, 'max_value': 5000},
            'expected': True
        },
        {
            'alert_type': 'CLIENT_CONCENTRATION',
            'current_value': 60,
            'threshold': {'max_percentage': 50},
            'expected': True
        },
        {
            'alert_type': 'INVOICE_OVERDUE',
            'current_value': 45,
            'threshold': {'max_days': 30},
            'expected': True
        }
    ]

    for case in test_cases:
        result = alert_configuration_service.validate_alert_threshold(
            case['alert_type'], 
            case['current_value'], 
            case['threshold']
        )
        assert result == case['expected']

def test_get_recommended_thresholds(alert_configuration_service):
    """Prueba obtención de umbrales recomendados"""
    # Probar diferentes tipos de alerta
    alert_types = [
        'REVENUE_DROP', 
        'CLIENT_CONCENTRATION', 
        'INVOICE_OVERDUE', 
        'HIGH_REVENUE_VOLATILITY',
        'UNKNOWN_ALERT_TYPE'
    ]

    for alert_type in alert_types:
        thresholds = alert_configuration_service.get_recommended_thresholds(alert_type)
        
        if alert_type != 'UNKNOWN_ALERT_TYPE':
            assert 'description' in thresholds
            assert 'default_threshold' in thresholds
        else:
            assert thresholds == {}

def test_suggest_notification_channels(alert_configuration_service):
    """Prueba sugerencia de canales de notificación"""
    # Probar diferentes tipos de alerta
    alert_types = [
        'REVENUE_DROP', 
        'CLIENT_CONCENTRATION', 
        'INVOICE_OVERDUE', 
        'HIGH_REVENUE_VOLATILITY',
        'UNKNOWN_ALERT_TYPE'
    ]

    for alert_type in alert_types:
        channels = alert_configuration_service.suggest_notification_channels(alert_type)
        
        # Verificar que siempre devuelve al menos un canal
        assert len(channels) > 0
        
        # Verificar que los canales son del tipo NotificationChannel
        assert all(isinstance(channel, NotificationChannel) for channel in channels)
        
        # Si es un tipo de alerta desconocido, debe devolver EMAIL por defecto
        if alert_type == 'UNKNOWN_ALERT_TYPE':
            assert channels == [NotificationChannel.EMAIL]
