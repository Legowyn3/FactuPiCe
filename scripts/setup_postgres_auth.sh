#!/bin/bash

# Cambiar la contraseña del usuario postgres
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Crear la base de datos si no existe
sudo -u postgres createdb -U postgres facturas 2>/dev/null || true

# Verificar la conexión
PGPASSWORD=postgres psql -U postgres -h localhost -d facturas -c "SELECT version();"
