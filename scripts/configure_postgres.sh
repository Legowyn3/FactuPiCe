#!/bin/bash

# Verificar que se está ejecutando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Este script debe ejecutarse como root (usando sudo)"
    exit 1
fi

# Configurar postgresql.conf
POSTGRESQL_CONF="/etc/postgresql/16/main/postgresql.conf"
echo "Configurando $POSTGRESQL_CONF..."
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" $POSTGRESQL_CONF
sed -i "s/#port = 5432/port = 5432/" $POSTGRESQL_CONF

# Configurar pg_hba.conf
PG_HBA_CONF="/etc/postgresql/16/main/pg_hba.conf"
echo "Configurando $PG_HBA_CONF..."
cat > $PG_HBA_CONF << EOL
# PostgreSQL Client Authentication Configuration File
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOL

# Reiniciar PostgreSQL
echo "Reiniciando PostgreSQL..."
systemctl restart postgresql

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 5

# Verificar el estado
echo "Verificando el estado de PostgreSQL..."
systemctl status postgresql

# Configurar la contraseña del usuario postgres
echo "Configurando la contraseña del usuario postgres..."
su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""

# Crear la base de datos si no existe
echo "Creando la base de datos facturas si no existe..."
su - postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'facturas'\" | grep -q 1 || psql -c \"CREATE DATABASE facturas;\""

echo "Configuración completada."
echo "Prueba la conexión con: psql -U postgres -h localhost -d facturas"
