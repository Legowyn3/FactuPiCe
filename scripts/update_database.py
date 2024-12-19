from sqlalchemy import create_engine, text
import os
import sys

# Añadir el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SQLALCHEMY_DATABASE_URL

def update_database():
    """Actualizar la base de datos con las nuevas columnas"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # Crear las nuevas columnas
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS apellidos VARCHAR;"))
        conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono VARCHAR;"))
        conn.commit()

if __name__ == "__main__":
    update_database()
    print("Base de datos actualizada correctamente")
