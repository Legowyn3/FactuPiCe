import pytest
from app.services.qr_service import QRService
from app.utils.aeat_errors import ValidationError
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import io

@pytest.fixture
def qr_service():
    """Fixture para el servicio QR."""
    return QRService()

def test_qr_service_init():
    """Test QRService initialization."""
    service = QRService()
    assert service.qr_size == 200

def test_generate_qr_code(qr_service):
    """Test QR code generation."""
    data = "https://test.ticketbai.com/12345"
    qr_bytes = qr_service.generate_qr_code(data)
    
    # Verificar que se generó el QR
    assert qr_bytes is not None
    assert len(qr_bytes) > 0
    
    # Verificar que es una imagen válida
    img = Image.open(io.BytesIO(qr_bytes))
    assert img.size == (200, 200)  # Verificar el tamaño
    assert img.mode == "RGB"  # Verificar el modo de color

def test_generate_qr_code_empty_data(qr_service):
    """Test QR code generation with empty data."""
    with pytest.raises(ValidationError):
        qr_service.generate_qr_code("")

def test_decode_qr_code(qr_service):
    """Test QR code decoding."""
    test_data = "https://test.ticketbai.com/12345"
    
    # Generar QR
    qr_bytes = qr_service.generate_qr_code(test_data)
    
    # Decodificar QR
    decoded_data = qr_service.decode_qr_code(qr_bytes)
    
    assert decoded_data == test_data

def test_decode_invalid_qr(qr_service):
    """Test decoding invalid QR code."""
    invalid_bytes = b"invalid data"
    
    with pytest.raises(ValidationError):
        qr_service.decode_qr_code(invalid_bytes)

def test_validate_qr_data(qr_service):
    """Test QR data validation."""
    
    # Datos válidos
    assert qr_service.validate_qr_data("https://test.ticketbai.com/12345") == True
    
    # Datos inválidos
    assert qr_service.validate_qr_data("") == False
    assert qr_service.validate_qr_data("http://invalid.com") == False
    assert qr_service.validate_qr_data("not a url") == False

def test_generate_qr_code_with_invalid_data(qr_service):
    """Prueba la generación de QR con datos inválidos."""
    with pytest.raises(ValidationError):
        qr_service.generate_qr_code("")

def test_validate_qr_data(qr_service):
    """Prueba la validación de datos de QR."""
    valid_data = "https://test.ticketbai.eus/12345"
    assert qr_service.validate_qr_data(valid_data) == True
    
    invalid_data = "invalid-url"
    assert qr_service.validate_qr_data(invalid_data) == False

def test_decode_qr_code(qr_service):
    """Prueba la decodificación de códigos QR."""
    test_data = "https://test.ticketbai.eus/12345"
    qr_image = qr_service.generate_qr_code(test_data)
    
    decoded_data = qr_service.decode_qr_code(qr_image)
    assert decoded_data == test_data

def test_decode_invalid_qr_code(qr_service):
    """Prueba la decodificación de códigos QR inválidos."""
    invalid_image = b"invalid image data"
    with pytest.raises(ValidationError):
        qr_service.decode_qr_code(invalid_image)

def test_qr_code_size(qr_service):
    """Prueba que el tamaño del código QR sea correcto."""
    test_data = "https://test.ticketbai.eus/12345"
    qr_image = qr_service.generate_qr_code(test_data)
    
    image = Image.open(io.BytesIO(qr_image))
    width, height = image.size
    
    # Verificar que el tamaño sea el esperado (por defecto 200x200)
    assert width == 200
    assert height == 200

def test_qr_code_format(qr_service):
    """Prueba que el formato del código QR sea PNG."""
    test_data = "https://test.ticketbai.eus/12345"
    qr_image = qr_service.generate_qr_code(test_data)
    
    image = Image.open(io.BytesIO(qr_image))
    assert image.format.lower() == 'png'

def test_qr_code_error_correction(qr_service):
    """Prueba que el código QR tenga corrección de errores."""
    test_data = "https://test.ticketbai.eus/12345"
    qr_image = qr_service.generate_qr_code(test_data)
    
    # Modificar algunos píxeles de la imagen no debería afectar la decodificación
    image = Image.open(io.BytesIO(qr_image))
    pixels = image.load()
    
    # Modificar algunos píxeles
    for i in range(10):
        pixels[i, i] = 0  # Negro
    
    # Guardar la imagen modificada
    modified_buffer = io.BytesIO()
    image.save(modified_buffer, format='PNG')
    modified_image = modified_buffer.getvalue()
    
    # Debería poder decodificarse aún con los píxeles modificados
    decoded_data = qr_service.decode_qr_code(modified_image)
    assert decoded_data == test_data
