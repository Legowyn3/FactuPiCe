# FactuPiCe - Sistema de Facturación

## Estado del Proyecto
**Versión:** 1.0.0  
**Estado:** En desarrollo  
**Última actualización:** Diciembre 2023

## Descripción
Sistema de facturación diseñado para autónomos y pequeñas empresas, con énfasis en seguridad y cumplimiento normativo.

## Estructura del Proyecto
```
backend/app/
├── api/                  # API endpoints específicos
├── auth/                 # Sistema de autenticación
├── backup/              # Sistema de respaldo
├── core/                # Funcionalidades core
├── models/              # Modelos de datos
├── routes/              # Rutas de la API
├── schemas/             # Esquemas Pydantic
├── security/            # Características de seguridad
├── services/            # Servicios de negocio
└── utils/               # Utilidades generales
```

## Características Implementadas
### Seguridad
- ✅ Autenticación JWT
- ✅ MFA (Multi-Factor Authentication)
- ✅ Rate Limiting
- ✅ Validación de contraseñas
- ✅ Auditoría de eventos
- ✅ Backup automático
- ✅ Middleware de seguridad HTTPS

### Facturación
- ✅ Gestión de facturas
- ✅ Firma digital
- ✅ Generación de PDF
- ✅ Validación VERI*FACTU
- ✅ Cálculos automáticos de IVA

### Clientes
- ✅ Gestión de clientes
- ✅ Historial de facturas por cliente

## Dependencias Principales
- FastAPI
- SQLAlchemy
- Pydantic
- PyJWT
- python-jose[cryptography]
- passlib[bcrypt]
- pyotp (MFA)
- python-multipart

## Configuración Necesaria
1. Variables de entorno (.env):
   ```
   DATABASE_URL=postgresql://user:pass@localhost/db
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. Base de datos:
   - PostgreSQL requerido
   - Ejecutar migraciones: `alembic upgrade head`

## Próximos Pasos
1. Implementar sistema de notificaciones
2. Añadir integración con TicketBAI
3. Desarrollar dashboard financiero
4. Implementar exportación a SII (AEAT)
5. Añadir tests automatizados

## Notas de Seguridad
- Todas las contraseñas se hashean con bcrypt
- Implementado rate limiting para prevenir ataques de fuerza bruta
- Logs de auditoría para todas las operaciones sensibles
- Backups automáticos diarios
- Validación estricta de datos de entrada

## Comandos Útiles
```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Ejecutar tests
pytest

# Crear backup manual
python -m app.backup.backup_manager

# Generar nueva migración
alembic revision --autogenerate -m "descripción"
```

## Documentación Adicional
- API docs: `/docs` o `/redoc`
- Swagger UI disponible en desarrollo
- Logs en `/logs/`
- Backups en `/backups/`

## Control de Versiones
- Repositorio: https://github.com/Legowyn3/FactuPiCe
- Rama principal: main
- Convención de commits: Conventional Commits
- Flujo de trabajo Git: GitFlow

## Guía de Contribución
- Fork del repositorio
- Crear rama feature/fix
- Seguir guía de estilo de código
- Crear Pull Request
- Tests requeridos para merge

## Entornos
- Desarrollo: http://localhost:8000
- Staging: [pendiente]
- Producción: [pendiente]

## Mantenimiento
- Actualización de dependencias: Mensual
- Revisión de seguridad: Quincenal
- Backup de base de datos: Diario
- Rotación de logs: Semanal

## Contacto
- Mantenedor principal: [Tu nombre]
- Email: [Tu email]
- Issues: GitHub Issues

## Métricas del Proyecto
### Calidad de Código
- Cobertura de tests: 75%
  - Unit tests: 80%
  - Integration tests: 70%
  - E2E tests: 60%
- Deuda técnica:
  - Bugs: 12 (3 críticos)
  - Code smells: 45
  - Duplicaciones: 4.5%
  - Complejidad ciclomática media: 15

### Rendimiento
- Tiempo medio de respuesta API: 150ms
- Throughput: 1000 req/min
- Tasa de errores: 0.5%
- Uso de memoria: 2.5GB promedio

## Arquitectura y Diseño
### Patrones Implementados
- Repository pattern para acceso a datos
- Factory pattern para creación de facturas
- Observer pattern para notificaciones
- Strategy pattern para cálculos fiscales

### Decisiones Técnicas (ADRs)
1. Uso de FastAPI vs Flask
   - Mayor rendimiento
   - Validación automática con Pydantic
   - Documentación automática OpenAPI
   
2. PostgreSQL vs MongoDB
   - Necesidad de transacciones ACID
   - Relaciones complejas entre entidades
   - Soporte para JSON nativo

3. Arquitectura de Microservicios
   - Facturación
   - Autenticación
   - Notificaciones
   - Reporting

## Roadmap Detallado
### Q1 2024
- Integración con SII (AEAT)
  - Desarrollo: 6 semanas
  - Testing: 2 semanas
  - Certificación: 4 semanas
- Sistema de notificaciones
  - Email: Semana 1-2
  - SMS: Semana 3-4
  - Push notifications: Semana 5-6

### Q2 2024
- Dashboard financiero
  - KPIs principales
  - Gráficos interactivos
  - Exportación a Excel
- TicketBAI
  - Desarrollo core: 8 semanas
  - Certificación: 4 semanas

## Guía de Desarrollo
### Estándares de Código
- PEP 8 para Python
- Docstrings obligatorios
- Type hints requeridos
- Máximo 80 caracteres por línea
- Tests unitarios para nueva funcionalidad

### Proceso de Code Review
1. Verificación automática
   - Linting
   - Type checking
   - Test coverage
2. Revisión manual
   - Arquitectura
   - Seguridad
   - Rendimiento
3. Criterios de aceptación
   - Tests pasando
   - No nuevos warnings
   - Documentación actualizada

## Monitorización y Alertas
### Métricas Críticas
- CPU > 80% durante 5 minutos
- Memoria > 90% durante 2 minutos
- Latencia API > 500ms
- Tasa de error > 1%

### Sistema de Logs
- ELK Stack
  - Logs de aplicación
  - Logs de sistema
  - Logs de seguridad
- Retención: 30 días
- Rotación: Diaria

## Procedimientos de Emergencia
### Escalado de Incidentes
1. Nivel 1: Equipo de desarrollo
2. Nivel 2: DevOps
3. Nivel 3: Arquitecto + PM

### Contactos Críticos
- Soporte 24/7: [teléfono]
- DevOps: [contacto]
- DPO: [contacto]
- Proveedor Cloud: [contacto]

## Costes y Recursos
### Infraestructura
- Servidores: 500€/mes
- Base de datos: 200€/mes
- CDN: 100€/mes
- Backup: 50€/mes

### Equipo
- 2 Backend developers
- 1 Frontend developer
- 1 DevOps
- 1 QA

## Estado de Integración
- CI/CD: [GitHub Actions/Jenkins/etc]
- Estado actual del pipeline: [badge]
- Calidad del código: [badge SonarQube]
- Licencia: [tipo]

## Requisitos Técnicos
- Versión de Python: ^3.10
- Versión de Node.js: [si aplica]
- Requisitos de sistema: [CPU/RAM/Disco]
- Servicios externos necesarios: [Redis/ElasticSearch/etc]

## Monitorización
- Sistema de logs: [ELK/Grafana/etc]
- Métricas de rendimiento: [herramienta]
- Alertas configuradas: [lista]
- Dashboard: [URL]

## Documentación Técnica
- Arquitectura: [link]
- API docs: [link]
- Diagramas: [link]
- Decisiones técnicas (ADRs): [link]

## Roadmap
- Q1 2024: [objetivos]
- Q2 2024: [objetivos]
- Q3 2024: [objetivos]
- Q4 2024: [objetivos]

## KPIs
- Tiempo de respuesta API: [ms]
- Uptime: [porcentaje]
- Usuarios activos: [número]
- Transacciones/día: [número]

## Incidentes y Resolución
- Proceso de escalado
- Contactos de emergencia
- Runbooks
- Post-mortems anteriores

## Costes y Recursos
- Infraestructura mensual: [coste]
- Servicios externos: [coste]
- Recursos humanos: [FTEs]
- ROI esperado: [estimación]

## Resumen del Proyecto
### Configuración del Entorno de Desarrollo
- [x] Configuración de scripts de instalación
- [x] Configuración de NVM y Node.js
- [x] Instalación de herramientas de desarrollo
- [x] Configuración de Docker
- [x] Configuración de permisos de npm

### Configuración de Base de Datos
- [x] Instalación de PostgreSQL
- [x] Script de configuración de base de datos
- [x] Migración inicial de esquema
- [x] Configuración de conexión TypeORM
- [x] Modelos de entidad base
  - [x] Usuario
  - [x] Cliente
  - [x] Factura
  - [x] Línea de Factura

### Monitoreo y Métricas
- [x] Integración de Prometheus
- [x] Configuración de métricas personalizadas
- [x] Servicio de monitoreo con métodos completos
- [ ] Configuración de exportación de métricas

### Próximos Pasos
1. Implementar servicios para entidades
2. Crear controladores REST
3. Configurar autenticación y autorización
4. Desarrollar lógica de negocio
5. Implementar validaciones
6. Configurar pruebas unitarias e integración

### Herramientas y Tecnologías
- NestJS
- TypeORM
- PostgreSQL
- Prometheus
- Docker
- TypeScript

### Notas de Desarrollo
- Enfoque en código limpio y mantenible
- Uso de TypeScript para tipado seguro
- Configuración modular
- Énfasis en seguridad y rendimiento

## Historial de Cambios
- 2024-12-20: Configuración inicial de modelos y monitoreo
