#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Función para instalar dependencias del sistema
install_system_dependencies() {
    echo -e "${YELLOW}Instalando dependencias del sistema...${NC}"

    # Actualizar lista de paquetes
    sudo apt-get update

    # Instalar herramientas de desarrollo
    local dev_tools=(
        "curl"
        "git"
        "wget"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
        "build-essential"
    )

    sudo apt-get install -y "${dev_tools[@]}"
}

# Función para instalar Node.js via NVM
install_nodejs() {
    echo -e "${YELLOW}Instalando Node.js via NVM...${NC}"

    # Descargar e instalar NVM
    if [ ! -d "$HOME/.nvm" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    fi

    # Cargar NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

    # Instalar versiones LTS de Node.js
    local node_versions=("18.19.0" "20.10.0")
    for version in "${node_versions[@]}"; do
        nvm install "$version"
    done

    # Establecer versión por defecto
    nvm alias default 18.19.0
    nvm use 18.19.0
}

# Función para instalar Docker
install_docker() {
    echo -e "${YELLOW}Instalando Docker...${NC}"

    # Verificar si Docker ya está instalado
    if ! command -v docker &> /dev/null; then
        # Eliminar versiones antiguas
        sudo apt-get remove -y docker docker-engine docker.io containerd runc

        # Configurar repositorio
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        # Actualizar e instalar Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

        # Añadir usuario al grupo docker
        sudo usermod -aG docker "$USER"
    else
        echo -e "${GREEN}Docker ya está instalado.${NC}"
    fi
}

# Función para instalar herramientas de desarrollo adicionales
install_dev_tools() {
    echo -e "${YELLOW}Instalando herramientas de desarrollo adicionales...${NC}"

    # Herramientas de desarrollo
    local additional_tools=(
        "postgresql"
        "postgresql-contrib"
        "python3-pip"
        "python3-venv"
        "openjdk-17-jdk"
    )

    sudo apt-get install -y "${additional_tools[@]}"

    # Configurar Python de forma segura
    python3 -m venv "$HOME/.python-venv"
    
    # Activar entorno virtual
    source "$HOME/.python-venv/bin/activate"

    # Instalar herramientas Python en entorno virtual
    pip install \
        pylint \
        black \
        mypy \
        bandit \
        safety

    # Desactivar entorno virtual
    deactivate

    # Configurar PostgreSQL
    sudo -u postgres createuser -s "$USER" 2>/dev/null || true
}

# Función para configurar Git
configure_git() {
    echo -e "${YELLOW}Configurando Git...${NC}"

    # Configuración global de Git
    git config --global user.name "Tu Nombre"
    git config --global user.email "tu.email@example.com"
    git config --global core.editor "code --wait"
    
    # Configurar commitizen
    git config --global commit.template ~/.gitmessage
    echo "feat(scope): descripción corta del cambio" > ~/.gitmessage
}

# Función principal
main() {
    echo -e "${GREEN}Iniciando configuración de entorno de desarrollo...${NC}"

    # Instalar dependencias
    install_system_dependencies

    # Instalar Node.js
    install_nodejs

    # Instalar Docker
    install_docker

    # Instalar herramientas adicionales
    install_dev_tools

    # Configurar Git
    configure_git

    echo -e "${GREEN}Configuración de entorno completada.${NC}"
    echo -e "${YELLOW}Reinicia tu terminal para aplicar todos los cambios.${NC}"
}

# Ejecutar script
main "$@"
