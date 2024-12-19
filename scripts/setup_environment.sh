#!/bin/bash

echo "Configurando el entorno de desarrollo..."

# Verificar si estamos ejecutando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Este script necesita privilegios de administrador."
    echo "Por favor, ejecuta: sudo ./scripts/setup_environment.sh"
    exit 1
fi

# Actualizar lista de paquetes
apt update

# Instalar dependencias del sistema
apt install -y python3-pip python3-venv postgresql postgresql-contrib

# Crear el entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activar el entorno virtual y instalar dependencias
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar la base de datos PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE facturas;" || true
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypassword';" || true
sudo -u postgres psql -c "ALTER ROLE myuser SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE myuser SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE facturas TO myuser;"

# Aplicar migraciones
alembic upgrade head

echo "Configuración completada con éxito."
echo "Para activar el entorno virtual, ejecuta: source venv/bin/activate"
