# FactuPiCe V2 - Sistema de Facturación

## Descripción
Sistema de facturación moderno y escalable desarrollado con NestJS, TypeScript y PostgreSQL.

## Requisitos Previos
- Node.js 18.x o superior
- npm 9.x o superior
- Docker (opcional)
- PostgreSQL 15

## Configuración del Entorno de Desarrollo

### Instalación de Dependencias
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/factupicev2.git
cd factupicev2

# Configurar entorno de desarrollo
./scripts/dev-environment-setup.sh
./scripts/npm-setup.sh

# Instalar dependencias del proyecto
cd backend
npm install
```

### Variables de Entorno
Crea un archivo `.env` en el directorio `backend` con las siguientes variables:
```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_contraseña
DATABASE_NAME=factupicev2
JWT_SECRET=tu_secreto_jwt
```

### Ejecución del Proyecto
```bash
# Desarrollo
npm run start:dev

# Producción
npm run build
npm run start:prod
```

## Scripts Disponibles
- `npm run lint`: Análisis de código estático
- `npm test`: Ejecutar pruebas unitarias
- `npm run test:cov`: Ejecutar pruebas con cobertura
- `scripts/vulnerability-scanner.sh`: Escanear vulnerabilidades
- `scripts/static-code-analysis.sh`: Análisis de código

## Estructura del Proyecto
```
factupicev2/
├── backend/
│   ├── src/
│   │   ├── modules/
│   │   ├── config/
│   │   └── main.ts
│   ├── test/
│   └── package.json
├── scripts/
│   ├── dev-environment-setup.sh
│   ├── npm-setup.sh
│   └── static-code-analysis.sh
└── monitoring/
    └── grafana-provisioning/
```

## Contribución
1. Crea un fork del repositorio
2. Crea una rama para tu característica
3. Haz commit con mensajes descriptivos
4. Abre un Pull Request

## Licencia
MIT License

## Contacto
- Nombre: Tu Nombre
- Email: tu.email@example.com
