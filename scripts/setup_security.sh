#!/bin/bash

echo "Configurando el entorno de seguridad..."

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "Error: Ejecute este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "Creando directorios..."
mkdir -p logs backups

# Configurar permisos
echo "Configurando permisos..."
chmod 700 logs backups
chmod 600 .env

# Aplicar migraciones
echo "Aplicando migraciones..."
alembic upgrade head

# Iniciar servicios de seguridad
echo "Iniciando servicios de seguridad..."
python3 scripts/test_security.py

echo "Configuración de seguridad completada."
