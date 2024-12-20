#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Variables de configuración
DB_NAME="factupicev2"
DB_USER="factupicev2"
DB_PASSWORD=$(openssl rand -base64 12)
DB_HOST="localhost"
DB_PORT="5432"

# Función para instalar PostgreSQL
install_postgresql() {
    echo -e "${YELLOW}Instalando PostgreSQL...${NC}"
    
    # Añadir repositorio oficial de PostgreSQL
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    # Actualizar e instalar PostgreSQL
    sudo apt-get update
    sudo apt-get install -y postgresql-15 postgresql-contrib-15
    
    echo -e "${GREEN}PostgreSQL instalado correctamente.${NC}"
}

# Función para configurar base de datos
configure_database() {
    echo -e "${YELLOW}Configurando base de datos ${DB_NAME}...${NC}"
    
    # Cambiar a usuario postgres
    sudo -u postgres psql <<EOF
-- Crear usuario
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- Crear base de datos
CREATE DATABASE ${DB_NAME} WITH OWNER ${DB_USER};

-- Configurar privilegios
ALTER USER ${DB_USER} WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};

-- Configurar extensiones
\c ${DB_NAME}
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
EOF

    echo -e "${GREEN}Base de datos configurada correctamente.${NC}"
}

# Función para configurar conexión segura
secure_postgresql() {
    echo -e "${YELLOW}Configurando seguridad de PostgreSQL...${NC}"
    
    # Modificar configuración de autenticación
    sudo sed -i 's/local\s\+all\s\+all\s\+peer/local all all md5/' /etc/postgresql/15/main/pg_hba.conf
    
    # Reiniciar servicio
    sudo systemctl restart postgresql
    
    echo -e "${GREEN}Configuración de seguridad aplicada.${NC}"
}

# Función para guardar credenciales
save_credentials() {
    local credentials_file="$HOME/.factupicev2_db_credentials"
    
    echo -e "${YELLOW}Guardando credenciales de forma segura...${NC}"
    
    # Crear archivo de credenciales con permisos restringidos
    umask 077
    cat > "$credentials_file" <<EOF
# Credenciales de Base de Datos FactuPiCe V2
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF

    echo -e "${GREEN}Credenciales guardadas en ${credentials_file}${NC}"
}

# Función para generar archivo .env
generate_env() {
    local env_file="/home/piqueras/Documentos/FactuPiCe/backend/.env"
    
    echo -e "${YELLOW}Generando archivo de configuración .env...${NC}"
    
    cat > "$env_file" <<EOF
# Configuración de Base de Datos
DATABASE_HOST=${DB_HOST}
DATABASE_PORT=${DB_PORT}
DATABASE_USER=${DB_USER}
DATABASE_PASSWORD=${DB_PASSWORD}
DATABASE_NAME=${DB_NAME}
DATABASE_SYNC=false
DATABASE_LOGGING=true

# Otras configuraciones del ejemplo anterior
JWT_SECRET=$(openssl rand -base64 32)
NODE_ENV=development
PORT=3000
EOF

    echo -e "${GREEN}Archivo .env generado en ${env_file}${NC}"
}

# Función principal
main() {
    echo -e "${GREEN}Iniciando configuración de base de datos FactuPiCe V2...${NC}"
    
    # Instalar PostgreSQL
    install_postgresql
    
    # Configurar base de datos
    configure_database
    
    # Securizar PostgreSQL
    secure_postgresql
    
    # Guardar credenciales
    save_credentials
    
    # Generar .env
    generate_env
    
    echo -e "${GREEN}Configuración de base de datos completada.${NC}"
    echo -e "${YELLOW}IMPORTANTE: Guarda las credenciales en un lugar seguro.${NC}"
}

# Ejecutar script
main "$@"
