from app.models.user import User
from app.models.factura import Factura
from app.security import get_password_hash
from datetime import datetime

def create_test_user(db):
    """Crear usuario de prueba en la base de datos"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_factura(db, user_id):
    """Crear factura de prueba en la base de datos"""
    factura = Factura(
        fecha=datetime.now().date(),
        numero="001",
        nif_cif_cliente="B12345678",
        base_imponible=1000.0,
        tipo_iva=21.0,
        cuota_iva=210.0,
        tipo_retencion=15.0,
        retencion=150.0,
        total_factura=1060.0,
        concepto="Factura de prueba",
        estado="pendiente",
        user_id=user_id
    )
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura
