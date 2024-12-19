from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import logging
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa, utils, padding
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.exceptions import InvalidSignature
from OpenSSL import crypto
import base64
from signxml import XMLSigner, XMLVerifier, SignatureConstructionMethod
from lxml import etree
import signxml
from ..utils.aeat_errors import SignatureError, ConfigurationError, ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Cambiar el nivel de logging a DEBUG

class SignatureService:
    def __init__(
        self,
        cert_path: Optional[str] = None,
        cert_password: Optional[str] = None,
        cert_format: str = 'pem'
    ):
        """
        Inicializa el servicio de firma.
        
        Args:
            cert_path: Ruta al certificado
            cert_password: Contraseña del certificado
            cert_format: Formato del certificado ('pem' o 'der')
        """
        self.cert_path = cert_path or os.getenv('CERT_PATH')
        self.cert_password = cert_password or os.getenv('CERT_PASSWORD')
        self.cert_format = cert_format.lower()
        
        if not self.cert_path:
            # Permitir certificado nulo para pruebas
            logger.warning("No se ha especificado la ruta del certificado. Se usará un certificado de prueba.")
            self.cert = None
            self.private_key = None
            return
        
        if not os.path.exists(self.cert_path):
            raise ConfigurationError(f"No se encuentra el certificado en la ruta: {self.cert_path}")
        
        try:
            self._load_certificate()
            self._validate_certificate_details()
        except Exception as e:
            logger.error(f"Error al inicializar el servicio de firma: {e}")
            raise

    def _load_certificate(self):
        """Carga el certificado y la clave privada."""
        try:
            with open(self.cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
                
                # Soporte para diferentes formatos de certificado
                if self.cert_format == 'pem':
                    self.cert = load_pem_x509_certificate(cert_data)
                elif self.cert_format == 'der':
                    self.cert = load_der_x509_certificate(cert_data)
                else:
                    raise ValueError(f"Formato de certificado no soportado: {self.cert_format}")
                
                cert_file.seek(0)
                self.private_key = serialization.load_pem_private_key(
                    cert_data,
                    password=self.cert_password.encode() if self.cert_password else None
                )
        except Exception as e:
            logger.error(f"Error al cargar el certificado: {e}")
            raise SignatureError(f"Error al cargar el certificado: {str(e)}")

    def _validate_certificate_details(self):
        """Validaciones adicionales del certificado."""
        now = datetime.now()
        
        # Verificar fechas de validez
        if self.cert.not_valid_before > now or self.cert.not_valid_after < now:
            logger.warning("Certificado caducado o aún no válido")
            raise SignatureError("El certificado no está vigente")
        
        # Verificar días restantes antes de la caducidad
        days_remaining = (self.cert.not_valid_after - now).days
        if days_remaining < 30:
            logger.warning(f"Quedan {days_remaining} días antes de la caducidad del certificado")

    def sign_xml(self, xml_content: str, include_certificate: bool = False) -> str:
        """
        Firma un documento XML.
        
        Args:
            xml_content: Contenido XML a firmar
            include_certificate: Si se debe incluir el certificado en la firma
            
        Returns:
            str: XML firmado
        """
        if self.cert is None or self.private_key is None:
            logger.warning("No se puede firmar XML sin certificado")
            return xml_content

        try:
            # Convertir el string XML a un objeto ElementTree
            root = etree.fromstring(xml_content.encode('utf-8'))
    
            signer = XMLSigner(
                method=SignatureConstructionMethod.enveloped,
                signature_algorithm="rsa-sha256",
                digest_algorithm="sha256",
                c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
            )
    
            # Configuración para incluir certificado si se solicita
            extra_args = {}
            if include_certificate:
                # Convertir el certificado a PEM si es necesario
                if isinstance(self.cert, x509.Certificate):
                    pem_cert = self.cert.public_bytes(encoding=serialization.Encoding.PEM)
                else:
                    pem_cert = self.cert
                extra_args['cert'] = pem_cert
    
            signed_root = signer.sign(
                root,
                key=self.private_key,
                **extra_args
            )
    
            return etree.tostring(signed_root, encoding='unicode', pretty_print=True)
    
        except Exception as e:
            logger.error(f"Error al firmar el XML: {e}")
            raise SignatureError(f"Error al firmar el XML: {str(e)}")

    def verify_signature(self, signed_xml):
        """
        Verifica la firma de un documento XML.

        Args:
            signed_xml (str or bytes or etree.Element): Documento XML firmado.

        Returns:
            bool: True si la firma es válida, False en caso contrario.
        """
        if self.cert is None:
            logger.warning("No se puede verificar la firma sin certificado")
            return False

        try:
            # Convertir el certificado a PEM si es necesario
            if isinstance(self.cert, x509.Certificate):
                pem_cert = self.cert.public_bytes(encoding=serialization.Encoding.PEM)
            else:
                pem_cert = self.cert

            # Convertir XML a bytes
            if isinstance(signed_xml, str):
                signed_xml = signed_xml.encode('utf-8')
            elif isinstance(signed_xml, etree.Element):
                signed_xml = etree.tostring(signed_xml)
            elif not isinstance(signed_xml, bytes):
                raise TypeError("signed_xml debe ser str, bytes o etree.Element")

            verified_data = XMLVerifier().verify(signed_xml, x509_cert=pem_cert)
            return True
        except Exception as e:
            logger.error(f"Error inesperado al verificar la firma: {e}")
            return False

    def get_certificate_info(self) -> dict:
        """
        Obtiene información detallada del certificado.
        
        Returns:
            dict: Información del certificado
        """
        if self.cert is None:
            logger.warning("No hay información de certificado disponible")
            return {}

        try:
            subject = self.cert.subject
            issuer = self.cert.issuer
            
            return {
                "subject": {attr.oid._name: attr.value for attr in subject},
                "issuer": {attr.oid._name: attr.value for attr in issuer},
                "serial_number": self.cert.serial_number,
                "not_before": self.cert.not_valid_before,
                "not_after": self.cert.not_valid_after,
                "key_type": "RSA" if isinstance(self.private_key, rsa.RSAPrivateKey) else "Unknown",
                "key_size": self.private_key.key_size
            }
            
        except Exception as e:
            logger.error(f"Error al obtener información del certificado: {e}")
            raise SignatureError(f"Error al obtener información del certificado: {str(e)}")

    def validate_certificate(self, cert_path: Optional[str] = None, cert_format: str = 'pem') -> bool:
        """
        Valida un certificado.
        
        Args:
            cert_path: Ruta al certificado. Si no se proporciona, usa el certificado actual
            cert_format: Formato del certificado
            
        Returns:
            bool: True si el certificado es válido
        """
        try:
            if not cert_path:
                cert_path = self.cert_path
            
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                
            # Cargar certificado según el formato
            if cert_format.lower() == 'pem':
                cert = load_pem_x509_certificate(cert_data)
            elif cert_format.lower() == 'der':
                cert = load_der_x509_certificate(cert_data)
            else:
                raise ValueError(f"Formato de certificado no soportado: {cert_format}")
            
            now = datetime.now()
            
            # Validaciones
            if cert.not_valid_before > now or cert.not_valid_after < now:
                logger.warning("Certificado caducado o aún no válido")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error en la validación del certificado: {e}")
            raise SignatureError(f"Error en la validación del certificado: {str(e)}")

    def get_certificate_expiration(self, cert_path: Optional[str] = None) -> datetime:
        """
        Obtiene la fecha de expiración del certificado.
        
        Args:
            cert_path: Ruta al certificado. Si no se proporciona, usa el certificado actual
            
        Returns:
            datetime: Fecha de expiración
        """
        if not cert_path:
            return self.cert.not_valid_after
        
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
            cert = load_pem_x509_certificate(cert_data)
        return cert.not_valid_after

    def get_days_until_expiration(self, cert_path: Optional[str] = None) -> int:
        """
        Calcula los días restantes hasta la expiración del certificado.
        
        Args:
            cert_path: Ruta al certificado. Si no se proporciona, usa el certificado actual
            
        Returns:
            int: Días restantes hasta la expiración
        """
        expiration_date = self.get_certificate_expiration(cert_path)
        days_remaining = (expiration_date - datetime.now()).days
        return max(0, days_remaining)

    def renew_certificate(self, new_cert_path: str, new_cert_password: Optional[str] = None):
        """
        Renueva el certificado del servicio.
        
        Args:
            new_cert_path: Ruta al nuevo certificado
            new_cert_password: Contraseña del nuevo certificado
        """
        try:
            # Validar el nuevo certificado
            if not self.validate_certificate(new_cert_path):
                raise SignatureError("El nuevo certificado no es válido")
            
            # Actualizar certificado y contraseña
            self.cert_path = new_cert_path
            self.cert_password = new_cert_password
            
            # Recargar certificado
            self._load_certificate()
            self._validate_certificate_details()
            
            logger.info("Certificado renovado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al renovar el certificado: {e}")
            raise SignatureError(f"Error al renovar el certificado: {str(e)}")
