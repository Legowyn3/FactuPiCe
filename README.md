<<<<<<< HEAD
# FactuPiCe
Proyecto Facturacion Autonomos
=======
# Sistema de Gestión de Facturas

## Descripción
Aplicación web para gestión integral de facturas con funcionalidades avanzadas de modelado fiscal.

## Características Principales
- 🔐 Autenticación de usuarios
- 📋 Gestión completa de facturas
- 💡 Cálculo automático de impuestos
- 📊 Generación de informes fiscales

## Requisitos Previos
- Python 3.9+
- pip
- virtualenv (opcional pero recomendado)

## Instalación

### 1. Clonar Repositorio
```bash
git clone https://github.com/tu_usuario/gestion-facturas.git
cd gestion-facturas
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Copiar `.env.example` a `.env` y personalizar configuraciones

### 5. Inicializar Base de Datos
```bash
flask db upgrade
flask init-db
flask create-admin
```

### 6. Ejecutar Aplicación
```bash
flask run
```

## Estructura del Proyecto
```
/app
├── models/         # Modelos de datos
├── routes/         # Rutas de la aplicación
├── services/       # Servicios y lógica de negocio
├── static/         # Archivos estáticos
└── templates/      # Plantillas HTML
```

## Contribuir
1. Fork del repositorio
2. Crear rama de características
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## Licencia
MIT License

## Contacto
- Email: soporte@gestionfacturas.com
- Twitter: @GestionFacturas
>>>>>>> c86aacc (Inicialización del proyecto FactuPiCe)
