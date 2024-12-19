# FactuPiCe - Backend

## Descripción
Backend para aplicación de gestión fiscal para autónomos y pequeñas empresas en España.

## Tecnologías
- NestJS
- TypeORM
- PostgreSQL
- Redis
- Docker
- Prometheus
- Grafana

## Requisitos
- Node.js 20+
- Docker
- Docker Compose

## Instalación

1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/factupi-ce-backend.git
cd factupi-ce-backend
```

2. Copiar archivo de configuración
```bash
cp env.example .env
```

3. Instalar dependencias
```bash
npm install
```

## Ejecución en Desarrollo
```bash
npm run start:dev
```

## Ejecución con Docker
```bash
docker-compose up --build
```

## Estructura del Proyecto
- `src/`: Código fuente
- `src/modules/`: Módulos de la aplicación
- `src/common/`: Utilidades y componentes compartidos
- `docker-compose.yml`: Configuración de servicios
- `Dockerfile`: Configuración de construcción de imagen

## Variables de Entorno
Configurar en `.env`:
- `DB_*`: Configuración de base de datos
- `JWT_*`: Configuración de autenticación
- `SMTP_*`: Configuración de email
- `FIREBASE_*`: Configuración de notificaciones push

## Comandos
- `npm run start`: Iniciar servidor
- `npm run build`: Compilar TypeScript
- `npm run test`: Ejecutar tests
- `npm run lint`: Verificar código

## Contribución
1. Fork del repositorio
2. Crear rama de feature
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## Licencia
MIT
