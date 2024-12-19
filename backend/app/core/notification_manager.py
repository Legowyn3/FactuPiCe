import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum, auto
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationChannel(Enum):
    EMAIL = auto()
    SMS = auto()
    PUSH = auto()
    WEBHOOK = auto()

class NotificationManager:
    def __init__(self, 
                 smtp_config: Optional[Dict[str, Any]] = None,
                 sms_provider: Optional[Any] = None,
                 push_notification_service: Optional[Any] = None):
        """
        Inicializar gestor de notificaciones.
        
        Args:
            smtp_config (Optional[Dict]): Configuración del servidor SMTP
            sms_provider (Optional[Any]): Servicio de envío de SMS
            push_notification_service (Optional[Any]): Servicio de notificaciones push
        """
        self.smtp_config = smtp_config or {}
        self.sms_provider = sms_provider
        self.push_service = push_notification_service
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def send_notification(
        self, 
        title: str, 
        message: str, 
        severity: str = 'INFO',
        channels: List[NotificationChannel] = None,
        recipients: Optional[List[str]] = None
    ):
        """
        Enviar notificación a través de múltiples canales.
        
        Args:
            title (str): Título de la notificación
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
            channels (List[NotificationChannel]): Canales de notificación
            recipients (Optional[List[str]]): Destinatarios
        """
        # Canales por defecto
        if channels is None:
            channels = [NotificationChannel.EMAIL]
        
        # Destinatarios por defecto (configurables)
        if recipients is None:
            recipients = self._get_default_recipients(severity)

        # Crear tareas para cada canal y destinatario
        tasks = []
        for channel in channels:
            for recipient in recipients:
                task = self._send_notification_by_channel(
                    channel, recipient, title, message, severity
                )
                tasks.append(task)
        
        # Ejecutar todas las tareas de notificación
        await asyncio.gather(*tasks)

    async def _send_notification_by_channel(
        self, 
        channel: NotificationChannel, 
        recipient: str, 
        title: str, 
        message: str, 
        severity: str
    ):
        """
        Enviar notificación por un canal específico.
        
        Args:
            channel (NotificationChannel): Canal de notificación
            recipient (str): Destinatario
            title (str): Título de la notificación
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
        """
        try:
            if channel == NotificationChannel.EMAIL:
                await self._send_email(recipient, title, message, severity)
            elif channel == NotificationChannel.SMS:
                await self._send_sms(recipient, title, message, severity)
            elif channel == NotificationChannel.PUSH:
                await self._send_push_notification(recipient, title, message, severity)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(recipient, title, message, severity)
        except Exception as e:
            self.logger.error(f"Error enviando notificación por {channel}: {e}")

    async def _send_email(self, recipient: str, title: str, message: str, severity: str):
        """
        Enviar notificación por correo electrónico.
        
        Args:
            recipient (str): Correo electrónico del destinatario
            title (str): Título del correo
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
        """
        if not self.smtp_config:
            self.logger.warning("Configuración SMTP no establecida")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('sender_email', 'noreply@empresa.com')
            msg['To'] = recipient
            msg['Subject'] = f"[{severity}] {title}"

            # Formatear cuerpo del correo
            body = f"""
            <html>
            <body>
                <h2>{title}</h2>
                <p>{message}</p>
                <small>Enviado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))

            async with aiosmtplib.SMTP(
                hostname=self.smtp_config.get('host', 'localhost'),
                port=self.smtp_config.get('port', 587)
            ) as smtp:
                await smtp.starttls()
                await smtp.login(
                    self.smtp_config.get('username'),
                    self.smtp_config.get('password')
                )
                await smtp.send_message(msg)

        except Exception as e:
            self.logger.error(f"Error enviando correo: {e}")

    async def _send_sms(self, recipient: str, title: str, message: str, severity: str):
        """
        Enviar notificación por SMS.
        
        Args:
            recipient (str): Número de teléfono
            title (str): Título del mensaje
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
        """
        if not self.sms_provider:
            self.logger.warning("Proveedor de SMS no configurado")
            return

        try:
            # Implementación específica según proveedor de SMS
            full_message = f"[{severity}] {title}\n{message}"
            await self.sms_provider.send_sms(recipient, full_message)
        except Exception as e:
            self.logger.error(f"Error enviando SMS: {e}")

    async def _send_push_notification(self, recipient: str, title: str, message: str, severity: str):
        """
        Enviar notificación push.
        
        Args:
            recipient (str): Token de dispositivo o usuario
            title (str): Título de la notificación
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
        """
        if not self.push_service:
            self.logger.warning("Servicio de notificaciones push no configurado")
            return

        try:
            await self.push_service.send_notification(
                recipient, 
                title=f"[{severity}] {title}", 
                body=message
            )
        except Exception as e:
            self.logger.error(f"Error enviando notificación push: {e}")

    async def _send_webhook_notification(self, recipient: str, title: str, message: str, severity: str):
        """
        Enviar notificación a través de webhook.
        
        Args:
            recipient (str): URL del webhook
            title (str): Título de la notificación
            message (str): Cuerpo del mensaje
            severity (str): Nivel de severidad
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'title': f"[{severity}] {title}",
                    'message': message,
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                }
                async with session.post(recipient, json=payload) as response:
                    if response.status != 200:
                        self.logger.error(f"Error en webhook: {response.status}")
        except Exception as e:
            self.logger.error(f"Error enviando webhook: {e}")

    def _get_default_recipients(self, severity: str) -> List[str]:
        """
        Obtener destinatarios predeterminados según severidad.
        
        Args:
            severity (str): Nivel de severidad
        
        Returns:
            Lista de destinatarios
        """
        # Configuración de destinatarios por defecto
        default_recipients = {
            'INFO': ['admin@empresa.com'],
            'MEDIUM': ['finanzas@empresa.com', 'admin@empresa.com'],
            'HIGH': ['gerencia@empresa.com', 'finanzas@empresa.com', 'admin@empresa.com'],
            'ERROR': ['soporte@empresa.com', 'gerencia@empresa.com']
        }
        
        return default_recipients.get(severity.upper(), ['admin@empresa.com'])
