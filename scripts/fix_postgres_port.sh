#!/bin/bash

# Verificar que se está ejecutando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Este script debe ejecutarse como root (usando sudo)"
    exit 1
fi

# Detener PostgreSQL
echo "Deteniendo PostgreSQL..."
systemctl stop postgresql

# Configurar postgresql.conf
POSTGRESQL_CONF="/etc/postgresql/16/main/postgresql.conf"
echo "Configurando puerto en $POSTGRESQL_CONF..."
sed -i "s/port = 5433/port = 5432/" $POSTGRESQL_CONF

# Reiniciar PostgreSQL
echo "Reiniciando PostgreSQL..."
systemctl start postgresql

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 5

# Verificar el estado
echo "Verificando el estado de PostgreSQL..."
pg_lsclusters

echo "Configuración completada."
echo "Prueba la conexión con: psql -U postgres -h localhost -d facturas"
