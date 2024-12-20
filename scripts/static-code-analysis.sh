#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para realizar análisis estático con ESLint
run_eslint_analysis() {
    local project_dir="$1"
    local output_file="${project_dir}/eslint-report.json"

    echo -e "${YELLOW}Ejecutando análisis estático con ESLint...${NC}"

    cd "$project_dir" || exit 1

    # Ejecutar ESLint con formato JSON
    npx eslint . \
        --ext .ts \
        --format json \
        --output-file "$output_file"

    # Analizar resultados
    local total_errors=$(jq '[.[].errorCount] | add' "$output_file")
    local total_warnings=$(jq '[.[].warningCount] | add' "$output_file")

    echo -e "${YELLOW}Resumen de ESLint:${NC}"
    echo -e "Total de errores: ${RED}$total_errors${NC}"
    echo -e "Total de advertencias: ${YELLOW}$total_warnings${NC}"

    # Mostrar detalles de errores críticos
    if [ "$total_errors" -gt 0 ]; then
        echo -e "${RED}Errores detectados:${NC}"
        jq -r '.[] | select(.errorCount > 0) | 
            "Archivo: \(.filePath)\n" + 
            (.messages | map("  - Línea \(.line): \(.message)") | join("\n"))' \
            "$output_file"
    fi
}

# Función para análisis de seguridad con Bandit
run_security_analysis() {
    local project_dir="$1"
    local output_file="${project_dir}/security-report.json"

    echo -e "${YELLOW}Ejecutando análisis de seguridad...${NC}"

    # Verificar si Bandit está instalado
    if ! command -v bandit &> /dev/null; then
        echo -e "${RED}Bandit no está instalado. Instalando...${NC}"
        pip install bandit
    fi

    # Ejecutar Bandit
    bandit \
        -r "$project_dir/src" \
        -f json \
        -o "$output_file" \
        --severity-level high

    # Analizar resultados de seguridad
    local high_issues=$(jq '.results | map(select(.issue_severity == "HIGH")) | length' "$output_file")
    local critical_issues=$(jq '.results | map(select(.issue_severity == "CRITICAL")) | length' "$output_file")

    echo -e "${YELLOW}Resumen de Análisis de Seguridad:${NC}"
    echo -e "Problemas de alta severidad: ${RED}$high_issues${NC}"
    echo -e "Problemas críticos: ${RED}$critical_issues${NC}"

    # Mostrar detalles de problemas de seguridad
    if [ "$high_issues" -gt 0 ] || [ "$critical_issues" -gt 0 ]; then
        echo -e "${RED}Problemas de seguridad detectados:${NC}"
        jq -r '.results[] | 
            "Archivo: \(.filename)\n" + 
            "Línea: \(.line_number)\n" + 
            "Severidad: \(.issue_severity)\n" + 
            "Descripción: \(.issue_text)\n"' \
            "$output_file"
    fi
}

# Función para análisis de complejidad ciclomática
run_complexity_analysis() {
    local project_dir="$1"
    local output_file="${project_dir}/complexity-report.json"

    echo -e "${YELLOW}Ejecutando análisis de complejidad...${NC}"

    # Usar ts-complexity para análisis de complejidad
    npx ts-complexity \
        "$project_dir/src/**/*.ts" \
        --max-complexity 15 \
        --format json \
        > "$output_file"

    # Analizar resultados de complejidad
    local complex_files=$(jq 'length' "$output_file")
    
    echo -e "${YELLOW}Resumen de Complejidad:${NC}"
    echo -e "Archivos con alta complejidad: ${RED}$complex_files${NC}"

    # Mostrar detalles de archivos complejos
    if [ "$complex_files" -gt 0 ]; then
        echo -e "${RED}Archivos con complejidad alta:${NC}"
        jq -r '.[] | 
            "Archivo: \(.file)\n" + 
            "Función: \(.function)\n" + 
            "Complejidad: \(.complexity)\n"' \
            "$output_file"
    fi
}

# Función principal
main() {
    local project_dir="${1:-.}"
    
    echo -e "${YELLOW}Iniciando análisis de código estático...${NC}"

    # Ejecutar análisis
    run_eslint_analysis "$project_dir"
    run_security_analysis "$project_dir"
    run_complexity_analysis "$project_dir"

    echo -e "${GREEN}Análisis de código completado.${NC}"
}

# Ejecutar script
main "$@"
