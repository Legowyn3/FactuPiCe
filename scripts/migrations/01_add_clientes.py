import os
import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from app.models import Base, Cliente, Factura
from app.database import engine

def migrate():
    try:
        # 1. Crear tabla de clientes
        Base.metadata.create_all(bind=engine, tables=[Cliente.__table__])
        print("✅ Tabla de clientes creada correctamente")

        # 2. Obtener datos de facturas existentes
        with engine.connect() as conn:
            # Verificar si la tabla facturas existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'facturas'
                );
            """))
            tabla_existe = result.scalar()

            if tabla_existe:
                # Obtener facturas existentes
                result = conn.execute(text("""
                    SELECT DISTINCT nif_cif_cliente 
                    FROM facturas;
                """))
                nifs_existentes = result.fetchall()

                # Crear clientes a partir de los NIFs existentes
                for (nif,) in nifs_existentes:
                    conn.execute(text("""
                        INSERT INTO clientes (nif_cif, nombre, direccion, codigo_postal, ciudad, provincia, activo)
                        VALUES (:nif, :nombre, :direccion, :cp, :ciudad, :provincia, :activo)
                        ON CONFLICT (nif_cif) DO NOTHING;
                    """), {
                        "nif": nif,
                        "nombre": f"Cliente {nif}",  # Nombre temporal
                        "direccion": "Pendiente de actualizar",
                        "cp": "00000",
                        "ciudad": "Pendiente",
                        "provincia": "Pendiente",
                        "activo": True
                    })
                print("✅ Clientes creados a partir de facturas existentes")

                # Añadir columna cliente_id a facturas si no existe
                conn.execute(text("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'facturas' AND column_name = 'cliente_id'
                        ) THEN
                            ALTER TABLE facturas ADD COLUMN cliente_id INTEGER;
                        END IF;
                    END $$;
                """))

                # Actualizar cliente_id en facturas
                conn.execute(text("""
                    UPDATE facturas f
                    SET cliente_id = c.id
                    FROM clientes c
                    WHERE f.nif_cif_cliente = c.nif_cif;
                """))

                # Hacer cliente_id NOT NULL y añadir foreign key
                conn.execute(text("""
                    ALTER TABLE facturas
                    ALTER COLUMN cliente_id SET NOT NULL,
                    ADD CONSTRAINT fk_cliente
                    FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id);
                """))

                # Eliminar columna nif_cif_cliente
                conn.execute(text("""
                    ALTER TABLE facturas
                    DROP COLUMN IF EXISTS nif_cif_cliente;
                """))
                print("✅ Tabla de facturas actualizada correctamente")

            conn.commit()

        print("✅ Migración completada exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        return False

if __name__ == "__main__":
    load_dotenv()
    migrate()
