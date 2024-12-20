#!/bin/bash

# Script para configurar y gestionar secretos de forma segura

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para generar una contraseña segura
generate_password() {
    openssl rand -base64 32
}

# Función para encriptar un secreto
encrypt_secret() {
    local secret="$1"
    node -e "
    const { secretsManager } = require('../dist/config/secrets.config');
    console.log(secretsManager.encrypt('$secret'));
    "
}

# Función para gestionar secretos
manage_secrets() {
    local env_file=".env"
    
    echo -e "${YELLOW}Configuración de Secretos para FactuPiCe V2${NC}"
    
    # Base de datos
    read -p "Introduzca el host de la base de datos (por defecto: localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Introduzca el puerto de la base de datos (por defecto: 5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -p "Introduzca el nombre de usuario de la base de datos: " DB_USERNAME
    read -sp "Introduzca la contraseña de la base de datos: " DB_PASSWORD
    echo
    
    # JWT
    JWT_SECRET=$(generate_password)
    JWT_EXPIRATION="7d"
    
    # Redis
    read -p "Introduzca el host de Redis (por defecto: localhost): " REDIS_HOST
    REDIS_HOST=${REDIS_HOST:-localhost}
    
    read -sp "Introduzca la contraseña de Redis (opcional): " REDIS_PASSWORD
    echo
    
    # Encriptar secretos
    ENCRYPTED_DB_PASSWORD=$(encrypt_secret "$DB_PASSWORD")
    ENCRYPTED_REDIS_PASSWORD=$(encrypt_secret "$REDIS_PASSWORD")
    ENCRYPTED_JWT_SECRET=$(encrypt_secret "$JWT_SECRET")
    
    # Generar archivo .env
    cat > "$env_file" << EOF
# Configuración de Base de Datos
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USERNAME=$DB_USERNAME
DB_PASSWORD=$ENCRYPTED_DB_PASSWORD

# Configuración JWT
JWT_SECRET=$ENCRYPTED_JWT_SECRET
JWT_EXPIRATION=$JWT_EXPIRATION

# Configuración Redis
REDIS_HOST=$REDIS_HOST
REDIS_PASSWORD=$ENCRYPTED_REDIS_PASSWORD

# Configuración de Entorno
NODE_ENV=development
PORT=3000
EOF

    echo -e "${GREEN}Archivo .env generado y secretos encriptados correctamente.${NC}"
}

# Ejecutar función principal
manage_secrets
