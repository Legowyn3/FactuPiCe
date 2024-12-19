from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, email_config: Optional[dict] = None):
        self.email_config = email_config or {}
        
    async def enviar_email(
        self, 
        destinatario: str, 
        asunto: str, 
        cuerpo: str, 
        archivos: List[str] = []
    ) -> bool:
        """
        Envía un email (simulado en desarrollo)
        """
        logger.info(f"Simulando envío de email a {destinatario}: {asunto}")
        return True 