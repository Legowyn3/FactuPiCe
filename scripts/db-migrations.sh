#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para generar migración
generate_migration() {
    local migration_name="$1"
    
    if [ -z "$migration_name" ]; then
        echo -e "${RED}Error: Debes proporcionar un nombre para la migración.${NC}"
        echo -e "${YELLOW}Uso: $0 generate <nombre_migracion>${NC}"
        exit 1
    }
    
    echo -e "${YELLOW}Generando migración: $migration_name${NC}"
    
    # Cambiar al directorio del backend
    cd "/home/piqueras/Documentos/FactuPiCe/backend"
    
    # Ejecutar generación de migración
    npx typeorm migration:create -n "$migration_name"
    
    echo -e "${GREEN}Migración generada exitosamente.${NC}"
}

# Función para ejecutar migraciones
run_migrations() {
    local migration_type="${1:-run}"
    
    echo -e "${YELLOW}Ejecutando migraciones (${migration_type})...${NC}"
    
    # Cambiar al directorio del backend
    cd "/home/piqueras/Documentos/FactuPiCe/backend"
    
    case "$migration_type" in
        "run")
            npx typeorm migration:run
            ;;
        "revert")
            npx typeorm migration:revert
            ;;
        "show")
            npx typeorm migration:show
            ;;
        *)
            echo -e "${RED}Tipo de migración no válido.${NC}"
            echo -e "${YELLOW}Opciones válidas: run, revert, show${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}Migraciones ejecutadas exitosamente.${NC}"
}

# Función para realizar respaldo de base de datos
backup_database() {
    local db_name="${1:-factupicev2}"
    local backup_dir="/home/piqueras/Documentos/FactuPiCe/backups/database"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Crear directorio de respaldos si no existe
    mkdir -p "$backup_dir"
    
    echo -e "${YELLOW}Realizando respaldo de base de datos ${db_name}...${NC}"
    
    # Realizar respaldo
    pg_dump -U "$USER" -d "$db_name" -f "${backup_dir}/${db_name}_${timestamp}.sql"
    
    # Comprimir respaldo
    gzip "${backup_dir}/${db_name}_${timestamp}.sql"
    
    echo -e "${GREEN}Respaldo de base de datos completado: ${backup_dir}/${db_name}_${timestamp}.sql.gz${NC}"
}

# Función principal
main() {
    local action="$1"
    shift
    
    case "$action" in
        "generate")
            generate_migration "$@"
            ;;
        "run")
            run_migrations "run"
            ;;
        "revert")
            run_migrations "revert"
            ;;
        "show")
            run_migrations "show"
            ;;
        "backup")
            backup_database "$@"
            ;;
        *)
            echo -e "${RED}Acción no válida.${NC}"
            echo -e "${YELLOW}Uso:${NC}"
            echo -e "  $0 generate <nombre_migracion>"
            echo -e "  $0 run"
            echo -e "  $0 revert"
            echo -e "  $0 show"
            echo -e "  $0 backup [nombre_base_datos]"
            exit 1
            ;;
    esac
}

# Ejecutar script
main "$@"
