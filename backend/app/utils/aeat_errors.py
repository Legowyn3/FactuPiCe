from typing import Dict, Optional

class AEATError(Exception):
    """Clase base para errores de AEAT."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

class SignatureError(AEATError):
    """Error en operaciones de firma digital."""
    def __init__(self, message: str):
        super().__init__("SIGN_ERROR", message)

class ValidationError(AEATError):
    """Error en validaciones."""
    def __init__(self, message: str):
        super().__init__("VAL_ERROR", message)

class CommunicationError(AEATError):
    """Error en comunicación con AEAT."""
    def __init__(self, message: str):
        super().__init__("COMM_ERROR", message)

class ConfigurationError(AEATError):
    """Error en configuración."""
    def __init__(self, message: str):
        super().__init__("CONF_ERROR", message)

class AuthenticationError(AEATError):
    """Error de autenticación con certificado."""
    def __init__(self, message: str):
        super().__init__("AUTH_ERROR", message)

class RateLimitError(AEATError):
    """Error por exceder el límite de peticiones."""
    def __init__(self, message: str):
        super().__init__("RATE_ERROR", message)

class MaintenanceError(AEATError):
    """Error por mantenimiento programado del servicio."""
    def __init__(self, message: str):
        super().__init__("MANT_ERROR", message)

# Mapeo de códigos de error de la AEAT
AEAT_ERROR_CODES = {
    # Errores de autenticación
    "AUTH001": "Certificado no válido o expirado",
    "AUTH002": "Certificado no autorizado para este servicio",
    "AUTH003": "Error en la firma de la petición",
    
    # Errores de validación
    "VAL001": "NIF/CIF no válido",
    "VAL002": "Importe no válido",
    "VAL003": "Fecha no válida",
    "VAL004": "Número de factura duplicado",
    "VAL005": "Serie de factura no válida",
    "VAL006": "Tipo de IVA no válido",
    
    # Errores de TicketBAI
    "TBAI001": "Error en la cadena de facturas",
    "TBAI002": "Hash anterior no válido",
    "TBAI003": "Identificador TBAI duplicado",
    "TBAI004": "Software no homologado",
    "TBAI005": "Error en la secuencia de facturas",
    "TBAI006": "Versión de TicketBAI no soportada",
    "TBAI007": "Error en el código QR",
    
    # Errores de comunicación
    "COM001": "Timeout en la conexión",
    "COM002": "Servicio no disponible",
    "COM003": "Error en la respuesta del servidor",
    
    # Errores de firma
    "SIGN001": "Error en la generación de la firma",
    "SIGN002": "Certificado de firma no válido",
    "SIGN003": "Error en el timestamp",
    
    # Errores de límite de peticiones
    "RATE001": "Límite de peticiones excedido",
    "RATE002": "Demasiadas peticiones desde esta IP",
    "RATE003": "Cuota diaria excedida",
    
    # Errores de mantenimiento
    "MANT001": "Servicio en mantenimiento programado",
    "MANT002": "Actualización del sistema en curso",
    
    # Errores de formato
    "FMT001": "Formato XML no válido",
    "FMT002": "Esquema XSD no válido",
    "FMT003": "Codificación de caracteres no válida"
}

def get_error_handler(error_code: str) -> AEATError:
    """Devuelve la excepción apropiada según el código de error."""
    error_message = AEAT_ERROR_CODES.get(error_code, "Error desconocido")
    
    if error_code.startswith("AUTH"):
        return AuthenticationError(error_message)
    elif error_code.startswith("VAL"):
        return ValidationError(error_message)
    elif error_code.startswith("TBAI"):
        return ValidationError(error_message)
    elif error_code.startswith("COM"):
        return CommunicationError(error_message)
    elif error_code.startswith("SIGN"):
        return SignatureError(error_message)
    elif error_code.startswith("RATE"):
        return RateLimitError(error_message)
    elif error_code.startswith("MANT"):
        return MaintenanceError(error_message)
    else:
        return AEATError("UNKNOWN_ERROR", error_message)

def parse_aeat_response(response: Dict) -> Optional[AEATError]:
    """Analiza la respuesta de la AEAT y devuelve un error si corresponde."""
    if response.get('Codigo') and response['Codigo'] != '0':
        error_code = response['Codigo']
        error_message = response.get('Descripcion', AEAT_ERROR_CODES.get(error_code, "Error desconocido"))
        return get_error_handler(error_code)
    return None

def is_retryable_error(error: AEATError) -> bool:
    """Determina si un error puede ser reintentado."""
    if isinstance(error, (AuthenticationError, ValidationError)):
        return False
        
    if isinstance(error, RateLimitError):
        return True
        
    if isinstance(error, CommunicationError):
        return True
        
    if isinstance(error, MaintenanceError):
        return True
        
    # Por defecto, no reintentar
    return False

def get_retry_delay(error: AEATError) -> float:
    """Sugiere un tiempo de espera base para el reintento según el tipo de error."""
    if isinstance(error, RateLimitError):
        return 60.0  # 1 minuto para errores de rate limit
        
    if isinstance(error, MaintenanceError):
        return 300.0  # 5 minutos para errores de mantenimiento
        
    if isinstance(error, CommunicationError):
        return 5.0  # 5 segundos para errores de comunicación
        
    return 1.0  # 1 segundo por defecto
