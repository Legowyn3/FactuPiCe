#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para configurar permisos de npm
configure_npm_permissions() {
    echo -e "${YELLOW}Configurando permisos de npm...${NC}"

    # Crear directorio para paquetes globales
    mkdir -p ~/.npm-global

    # Configurar npm para usar directorio de usuario
    npm config set prefix '~/.npm-global'

    # Actualizar PATH en archivos de configuración del shell
    update_shell_config() {
        local shell_config="$1"
        if [ -f "$shell_config" ]; then
            # Verificar si ya existe la configuración
            if ! grep -q "export PATH=~/.npm-global/bin:$PATH" "$shell_config"; then
                echo "export PATH=~/.npm-global/bin:$PATH" >> "$shell_config"
                echo -e "${GREEN}Actualizado: $shell_config${NC}"
            fi
        fi
    }

    # Actualizar configuraciones de shells
    update_shell_config "$HOME/.bashrc"
    update_shell_config "$HOME/.zshrc"
    update_shell_config "$HOME/.profile"

    # Recargar configuración
    source ~/.bashrc 2>/dev/null
    source ~/.zshrc 2>/dev/null
    source ~/.profile 2>/dev/null

    echo -e "${GREEN}Configuración de permisos de npm completada.${NC}"
}

# Función para instalar herramientas de desarrollo globales
install_dev_tools() {
    echo -e "${YELLOW}Instalando herramientas de desarrollo globales...${NC}"

    # Usar npm install local para evitar problemas de permisos
    local tools=(
        "eslint"
        "typescript"
        "ts-node"
        "@nestjs/cli"
        "jest"
        "npm-check-updates"
        "prettier"
        "commitizen"
        "standard-version"
    )

    # Crear directorio local para paquetes globales
    mkdir -p ~/.npm-local-global

    # Instalar herramientas
    for tool in "${tools[@]}"; do
        echo -e "${YELLOW}Instalando: $tool${NC}"
        npm install --prefix ~/.npm-local-global -g "$tool"
        
        # Verificar instalación
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ $tool instalado correctamente${NC}"
        else
            echo -e "${RED}✗ Error instalando $tool${NC}"
        fi
    done

    # Configuración adicional de herramientas
    echo -e "${YELLOW}Configurando herramientas...${NC}"
    
    # Configuración de ESLint
    ~/.npm-local-global/bin/eslint --init 2>/dev/null

    # Configuración de Commitizen
    ~/.npm-local-global/bin/commitizen init cz-conventional-changelog --save-dev --save-exact 2>/dev/null

    echo -e "${GREEN}Instalación de herramientas completada.${NC}"
}

# Función para verificar y actualizar npm
update_npm() {
    echo -e "${YELLOW}Verificando versión de npm...${NC}"
    
    # Obtener versión actual
    local current_version=$(npm --version)
    
    # Actualizar npm de forma segura
    npm install -g npm@latest --prefix ~/.npm-local-global
    
    echo -e "${GREEN}Npm actualizado de $current_version a $(~/.npm-local-global/bin/npm --version)${NC}"
}

# Función principal
main() {
    echo -e "${YELLOW}Iniciando configuración de entorno de desarrollo...${NC}"

    # Actualizar npm
    update_npm

    # Configurar permisos
    configure_npm_permissions

    # Instalar herramientas
    install_dev_tools

    echo -e "${GREEN}Configuración de entorno completada.${NC}"
}

# Ejecutar script
main "$@"
