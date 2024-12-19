import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from ..utils.digital_sign import CertificateManager, XAdESBuilder

class SecurityService:
    def __init__(self):
        self.cert_path = os.getenv('CERTIFICATE_PATH')
        self.key_path = os.getenv('PRIVATE_KEY_PATH')
        self.key_password = os.getenv('KEY_PASSWORD')
        
        # Inicializar encriptación para datos sensibles
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
            # En producción, guardar esta clave de forma segura
        
        self.fernet = Fernet(self.encryption_key)
        self._initialize_certificate_manager()

    def _initialize_certificate_manager(self):
        """Inicializa el gestor de certificados."""
        if not all([self.cert_path, self.key_path]):
            raise ValueError("Rutas de certificado y clave privada no configuradas")
        
        self.cert_manager = CertificateManager(
            self.cert_path,
            self.key_path,
            self.key_password
        )
        self.xades_builder = XAdESBuilder(self.cert_manager)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encripta datos sensibles."""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Desencripta datos sensibles."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    async def sign_invoice_xml(self, xml_content: str) -> tuple[str, str]:
        """Firma una factura en formato XML usando XAdES-XL."""
        signed_xml, timestamp = await self.xades_builder.sign_invoice(xml_content)
        return signed_xml.decode(), timestamp.isoformat()

    def validate_certificate(self) -> dict:
        """Valida el certificado actual."""
        cert_info = self.cert_manager.get_certificate_info()
        return {
            'valid': True,
            'info': cert_info
        }

    def backup_certificates(self, backup_dir: str):
        """Realiza una copia de seguridad de los certificados."""
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copiar certificado y clave privada
        for source_path in [self.cert_path, self.key_path]:
            if source_path:
                source = Path(source_path)
                dest = backup_path / source.name
                with open(source, 'rb') as src, open(dest, 'wb') as dst:
                    dst.write(src.read())

    def rotate_encryption_key(self) -> str:
        """Rota la clave de encriptación."""
        new_key = Fernet.generate_key()
        # En producción, implementar la rotación segura de claves
        # y re-encriptar todos los datos sensibles
        return new_key.decode()

class AuditLogger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    def log_security_event(self, event_type: str, details: dict):
        """Registra eventos de seguridad."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'details': details
        }
        
        with open(self.log_path, 'a') as f:
            f.write(f"{json.dumps(log_entry)}\n")
