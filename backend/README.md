# FactuPiCe - Backend

## Descripción
Backend de la aplicación de facturación para autónomos, desarrollado con NestJS y TypeORM.

## Requisitos Previos
- Node.js (v16 o superior)
- PostgreSQL (v12 o superior)
- npm o yarn

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/factupi-ce.git
cd factupi-ce/backend
```

2. Instalar dependencias
```bash
npm install
```

3. Configurar variables de entorno
Crea un archivo `.env` basado en `.env.example` y configura tus variables:
- `DB_HOST`
- `DB_PORT`
- `DB_USERNAME`
- `DB_PASSWORD`
- `DB_DATABASE`
- `JWT_SECRET`

## Comandos Disponibles

- `npm run start`: Iniciar servidor en modo producción
- `npm run start:dev`: Iniciar servidor en modo desarrollo
- `npm run migration:generate`: Generar nueva migración
- `npm run migration:run`: Ejecutar migraciones pendientes
- `npm run test`: Ejecutar pruebas unitarias
- `npm run test:e2e`: Ejecutar pruebas de integración

## Estructura del Proyecto
- `src/`: Código fuente
  - `modules/`: Módulos de la aplicación
  - `database/`: Migraciones y configuración de base de datos
  - `common/`: Utilidades y componentes compartidos

## Tecnologías Principales
- NestJS
- TypeORM
- PostgreSQL
- Passport.js (autenticación)
- Jest (testing)

## Contribución
1. Hacer fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia
MIT
