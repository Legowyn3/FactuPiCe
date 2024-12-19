import os
import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.models.base import Base
from app.database import engine
from app.models import Cliente, Factura

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear las tablas: {str(e)}")

if __name__ == "__main__":
    create_tables()
