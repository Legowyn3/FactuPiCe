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
