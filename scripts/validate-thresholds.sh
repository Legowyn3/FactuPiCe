#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para validar umbrales
validate_thresholds() {
    local thresholds_file="$1"
    local errors=0

    echo -e "${YELLOW}Validando umbrales de monitoreo...${NC}"

    # Validar umbrales del sistema
    validate_numeric_threshold "system.cpu_usage_warning" 0 100
    validate_numeric_threshold "system.cpu_usage_critical" 0 100
    validate_numeric_threshold "system.memory_usage_warning" 0 100
    validate_numeric_threshold "system.memory_usage_critical" 0 100
    validate_numeric_threshold "system.disk_usage_warning" 0 100
    validate_numeric_threshold "system.disk_usage_critical" 0 100

    # Validar umbrales de red
    validate_numeric_threshold "network.connection_timeout_warning" 0 5000
    validate_numeric_threshold "network.connection_timeout_critical" 0 5000
    validate_numeric_threshold "network.packet_loss_warning" 0 100
    validate_numeric_threshold "network.packet_loss_critical" 0 100

    # Validar umbrales de aplicación
    validate_numeric_threshold "application.clientes.creation_failure_rate_warning" 0 100
    validate_numeric_threshold "application.clientes.creation_failure_rate_critical" 0 100
    validate_numeric_threshold "application.clientes.response_time_warning" 0 5000
    validate_numeric_threshold "application.clientes.response_time_critical" 0 5000
    validate_numeric_threshold "application.clientes.cache_hit_rate_warning" 0 100
    validate_numeric_threshold "application.clientes.cache_hit_rate_critical" 0 100

    # Validar consistencia de umbrales
    validate_threshold_consistency "system.cpu_usage_warning" "system.cpu_usage_critical"
    validate_threshold_consistency "system.memory_usage_warning" "system.memory_usage_critical"
    validate_threshold_consistency "system.disk_usage_warning" "system.disk_usage_critical"

    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}Validación de umbrales completada sin errores.${NC}"
        return 0
    else
        echo -e "${RED}Se encontraron $errors errores en la configuración de umbrales.${NC}"
        return 1
    fi
}

# Función para validar un umbral numérico
validate_numeric_threshold() {
    local threshold_path="$1"
    local min_value="$2"
    local max_value="$3"

    # Extraer valor usando yq
    local value=$(yq e ".$threshold_path" /home/piqueras/Documentos/FactuPiCe/monitoring/alert-thresholds.yml)

    # Validar que el valor sea un número
    if [[ ! "$value" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error: $threshold_path debe ser un número entero.${NC}"
        ((errors++))
        return 1
    fi

    # Validar rango
    if (( $(echo "$value < $min_value" | bc -l) )) || (( $(echo "$value > $max_value" | bc -l) )); then
        echo -e "${RED}Error: $threshold_path debe estar entre $min_value y $max_value.${NC}"
        ((errors++))
        return 1
    fi

    echo -e "${GREEN}✓ $threshold_path: $value${NC}"
    return 0
}

# Función para validar consistencia entre umbrales
validate_threshold_consistency() {
    local warning_path="$1"
    local critical_path="$2"

    local warning_value=$(yq e ".$warning_path" /home/piqueras/Documentos/FactuPiCe/monitoring/alert-thresholds.yml)
    local critical_value=$(yq e ".$critical_path" /home/piqueras/Documentos/FactuPiCe/monitoring/alert-thresholds.yml)

    if (( $(echo "$warning_value >= $critical_value" | bc -l) )); then
        echo -e "${RED}Error: $warning_path debe ser menor que $critical_path.${NC}"
        ((errors++))
        return 1
    fi

    return 0
}

# Ejecutar validación
validate_thresholds
