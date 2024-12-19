import os
import pytest
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from app.services.signature_service import SignatureService
from app.utils.aeat_errors import SignatureError, ConfigurationError

def generate_test_certificate(valid_days=365):
    """Genera un certificado de prueba."""
    # Generar clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Generar certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"ES"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Madrid"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Madrid"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"testuser")
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.now()
    ).not_valid_after(
        datetime.now() + timedelta(days=valid_days)
    ).sign(private_key, hashes.SHA256())
    
    return cert, private_key

def save_certificate_to_file(cert, private_key, path, password=None):
    """Guarda un certificado y clave privada en un archivo."""
    with open(path, 'wb') as f:
        # Guardar certificado y clave privada en formato PEM
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption() if not password else 
            serialization.BestAvailableEncryption(password.encode())
        ))
    return path

@pytest.fixture
def test_cert_path(tmp_path):
    """Fixture para generar un certificado de prueba."""
    cert, private_key = generate_test_certificate()
    cert_path = tmp_path / "test_cert.pem"
    save_certificate_to_file(cert, private_key, cert_path)
    return str(cert_path)

@pytest.fixture
def signature_service(test_cert_path):
    """Fixture para crear un SignatureService de prueba."""
    return SignatureService(cert_path=test_cert_path)

def test_signature_service_initialization(test_cert_path):
    """Test de inicialización del servicio de firma."""
    service = SignatureService(cert_path=test_cert_path)
    assert service.cert_path == test_cert_path
    assert service.cert is not None
    assert service.private_key is not None

def test_signature_service_invalid_cert_path():
    """Test de inicialización con ruta de certificado inválida."""
    with pytest.raises(ConfigurationError):
        SignatureService(cert_path="/ruta/inexistente/certificado.pem")

def test_sign_xml(signature_service):
    """Test de firma de XML."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <data>Datos de prueba</data>
    </root>"""
    
    signed_xml = signature_service.sign_xml(xml_content)
    
    assert signed_xml is not None
    assert "Signature" in signed_xml
    assert len(signed_xml) > len(xml_content)

def test_verify_signature(signature_service):
    """Test de verificación de firma."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <data>Datos de prueba</data>
    </root>"""
    
    signed_xml = signature_service.sign_xml(xml_content)
    
    # Verificar la firma
    assert signature_service.verify_signature(signed_xml) == True

def test_get_certificate_info(signature_service):
    """Test de obtención de información del certificado."""
    info = signature_service.get_certificate_info()
    
    assert isinstance(info, dict)
    assert "subject" in info
    assert "issuer" in info
    assert "serial_number" in info
    assert "not_before" in info
    assert "not_after" in info
    assert "key_type" in info
    assert "key_size" in info

def test_validate_certificate(test_cert_path):
    """Test de validación de certificado."""
    service = SignatureService(cert_path=test_cert_path)
    
    # Validar el certificado de prueba
    assert service.validate_certificate(test_cert_path) == True

def test_get_days_until_expiration(signature_service, test_cert_path):
    """Test de obtención de días hasta la expiración."""
    days = signature_service.get_days_until_expiration(test_cert_path)
    
    assert isinstance(days, int)
    assert days > 0

def test_sign_xml_with_certificate_inclusion(signature_service):
    """Test de firma de XML con inclusión de certificado."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <root>
        <data>Datos de prueba</data>
    </root>"""
    
    signed_xml = signature_service.sign_xml(xml_content, include_certificate=True)
    
    assert signed_xml is not None
    assert "Signature" in signed_xml
    assert "X509Certificate" in signed_xml

def test_renew_certificate(signature_service, test_cert_path):
    """Test de renovación de certificado."""
    # Generar un nuevo certificado de prueba
    new_cert, new_private_key = generate_test_certificate(valid_days=365)
    new_cert_path = save_certificate_to_file(new_cert, new_private_key, test_cert_path + "_new")
    
    # Renovar certificado
    signature_service.renew_certificate(new_cert_path)
    
    # Verificar que el certificado se ha actualizado
    assert signature_service.cert_path == new_cert_path
    assert signature_service.validate_certificate() == True
