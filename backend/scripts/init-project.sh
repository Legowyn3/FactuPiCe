#!/bin/bash

# Script de inicialización para FactuPiCe Backend

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# Función para mostrar mensajes de error
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    error_exit "Este script debe ejecutarse en el directorio raíz del proyecto backend"
fi

# Limpiar instalaciones previas
echo -e "${YELLOW}Limpiando instalaciones previas...${NC}"
rm -rf node_modules
rm -f package-lock.json

# Instalar dependencias
echo -e "${YELLOW}Instalando dependencias...${NC}"
npm install || error_exit "Error al instalar dependencias"

# Generar archivo .env si no existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Generando archivo .env de ejemplo...${NC}"
    cp .env.example .env
fi

# Ejecutar migraciones
echo -e "${YELLOW}Ejecutando migraciones de base de datos...${NC}"
npm run migration:run || error_exit "Error al ejecutar migraciones"

# Compilar proyecto
echo -e "${YELLOW}Compilando proyecto...${NC}"
npm run build || error_exit "Error al compilar el proyecto"

# Mensaje de éxito
echo -e "${GREEN}✅ Proyecto inicializado correctamente${NC}"
echo -e "${GREEN}Puedes iniciar el servidor con:${NC}"
echo -e "  npm run start:dev"
