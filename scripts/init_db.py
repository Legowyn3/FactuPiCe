import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Crear cursor
    cur = conn.cursor()
    
    try:
        # Crear base de datos si no existe
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'facturas'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE facturas')
            print("Base de datos 'facturas' creada exitosamente")
        else:
            print("La base de datos 'facturas' ya existe")
            
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()
