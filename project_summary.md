# FactuPiCe: Aplicación de Facturación para Autónomos y Empresas

## 📋 Descripción General
FactuPiCe es una aplicación de facturación diseñada específicamente para autónomos y empresas en España, cumpliendo con las regulaciones fiscales españolas.

## 🏗️ Estructura del Proyecto
```
FactuPiCe/
│
├── backend/                # Backend de la aplicación
│   ├── src/                # Código fuente del backend
│   │   ├── main.ts         # Punto de entrada principal
│   │   ├── database/       # Configuraciones de base de datos
│   │   │   ├── migrations/ # Migraciones de TypeORM
│   │   │   └── data-source.ts # Configuración de conexión a base de datos
│   │   ├── entities/       # Modelos de entidad
│   │   └── modules/        # Módulos de negocio
│   ├── config/             # Configuraciones del proyecto
│   └── tests/              # Pruebas unitarias y de integración
│
├── frontend/               # Frontend de la aplicación
│   ├── src/                # Código fuente del frontend
│   └── public/             # Recursos públicos
│
└── docs/                   # Documentación del proyecto
```

## 🛠️ Tecnologías Principales
- **Backend**: 
  - Lenguaje: TypeScript 4.9+
  - Framework: NestJS 9.x
  - ORM: TypeORM 0.3.x
  - Base de Datos: PostgreSQL 13+
- **Autenticación**: 
  - JWT (JSON Web Tokens)
  - Estrategia de autenticación con Passport.js
- **Frontend**: (Por determinar)

## 🔍 Estado Actual del Desarrollo

### Progreso Técnico Detallado
#### Backend
- [x] Configuración inicial de NestJS
- [x] Configuración de TypeORM
- [x] Migración inicial de base de datos
- [x] Modelo de entidades de Usuario y Notificaciones
- [ ] Implementación de controladores de autenticación
- [ ] Lógica de negocio para gestión de usuarios

#### Modelos de Datos
1. **Modelo de Usuario**
   - Campos: 
     - `id`: Identificador único
     - `email`: Correo electrónico (único)
     - `password`: Contraseña encriptada
     - `role`: Rol de usuario
     - `pushToken`: Token para notificaciones push
     - `createdAt`: Fecha de creación
     - `updatedAt`: Fecha de última actualización

2. **Modelo de Notificaciones**
   - Campos:
     - `id`: Identificador único
     - `title`: Título de la notificación
     - `content`: Contenido
     - `type`: Tipo de notificación
     - `channel`: Canal de envío
     - `userId`: Usuario destinatario
     - `isRead`: Estado de lectura
     - `createdAt`: Fecha de creación

### Configuración de Desarrollo

#### Requisitos Previos
- Node.js 18.x
- npm 9.x
- PostgreSQL 13+
- Docker (opcional)

#### Scripts de NPM Disponibles
- `npm run start`: Iniciar servidor en modo desarrollo
- `npm run build`: Compilar proyecto
- `npm run migration:create`: Crear nueva migración
- `npm run migration:generate`: Generar archivos de migración basados en cambios
- `npm run migration:run`: Ejecutar migraciones pendientes
- `npm run migration:revert`: Revertir última migración
- `npm run test`: Ejecutar pruebas unitarias

#### Configuración de Base de Datos
- **Archivo de Configuración**: `typeorm.config.ts`
- **Características**:
  * Configuración dinámica basada en entorno
  * Soporte para desarrollo y producción
  * Conexión segura con base de datos PostgreSQL
  * Manejo de migraciones y entidades
  * Registro de consultas y errores

**Configuraciones de Entorno**:
- `development`: 
  * `synchronize`: true
  * Logging detallado
- `production`:
  * `synchronize`: false
  * Conexión SSL
  * Logging mínimo

### 🔒 Estrategias de Seguridad
- **Autenticación**:
  - JWT con tokens de acceso y refresh
  - Encriptación de contraseñas con bcrypt
  - Validación de tokens en cada solicitud
- **Protección de Datos**:
  - Campos sensibles excluidos de respuestas
  - Validación de entrada de datos
  - Gestión de permisos basada en roles

## 🚨 Puntos Pendientes
1. Completar implementación de autenticación
2. Desarrollar lógica de generación de facturas
3. Integración con servicios externos
4. Definir estrategia de frontend
5. Implementar pruebas de integración

## 🎯 Próximos Pasos
- Implementar controladores de usuarios
- Desarrollar servicio de notificaciones
- Configurar integración continua
- Definir estrategia de despliegue

## 📊 Métricas Técnicas
- Cobertura de pruebas: Por definir
- Tiempo de respuesta del API: Por medir
- Complejidad ciclomática: Por evaluar

## 🔍 Puntos de Atención
- Revisar configuraciones de seguridad
- Optimizar consultas de base de datos
- Validar cumplimiento de normativas fiscales
- Documentar API

## 📅 Historial de Desarrollo
- **Inicio del Proyecto**: (Fecha de inicio)
- **Última Actualización**: 19 de Diciembre de 2024
- **Versión Actual**: 0.1.0 (Desarrollo)

## 💡 Notas Adicionales
- Mantener actualizada la documentación
- Revisar regularmente la configuración de seguridad
- Estar atento a actualizaciones de dependencias

## 🔍 Casos de Uso Detallados

### 👤 Flujo de Autenticación de Usuario

#### Caso de Uso: Registro de Autónomo
**Descripción**: Un nuevo usuario autónomo se registra en la plataforma

**Pasos del Flujo**:
1. Usuario accede a pantalla de registro
2. Introduce datos personales:
   - Nombre completo
   - Email
   - Contraseña
   - NIF/CIF
3. Sistema valida:
   - Formato de email
   - Complejidad de contraseña
   - Validez de NIF/CIF
4. Genera perfil de usuario
5. Envía email de confirmación

**Validaciones**:
- Email único en sistema
- Contraseña: 
  * Mínimo 12 caracteres
  * Combinación de mayúsculas, minúsculas, números y símbolos
- NIF/CIF verificado contra API oficial

### 🔒 Documentación de API

#### Información General de API
- **Versión de API**: `v1.0.0`
- **Prefijo de Endpoints**: `/api/v1`
- **Seguridad**: 
  * Todos los endpoints requieren autenticación JWT
  * Uso de HTTPS obligatorio
  * Protección contra ataques CSRF
  * Límite de solicitudes por IP

#### Endpoints de Autenticación

##### 1. Registro de Usuario
- **URL**: `/api/v1/auth/register`
- **Método**: `POST`
- **Autenticación**: No requiere
- **Seguridad Adicional**: 
  * Protección contra ataques de fuerza bruta
  * Validación de reCAPTCHA

**Ejemplo de Solicitud**:
```json
{
  "email": "autonomo@ejemplo.com",
  "password": "Fact_Pi_C3_2024!",
  "fullName": "Juan Pérez González",
  "taxIdentificationNumber": "12345678A",
  "businessType": "autonomo"
}
```

**Respuestas**:
- `201 Created`: Registro exitoso
  ```json
  {
    "userId": "abc123",
    "email": "autonomo@ejemplo.com",
    "confirmationToken": "token_generado"
  }
  ```
- `400 Bad Request`: Error en validación
  ```json
  {
    "error": "Validation Failed",
    "code": "INVALID_INPUT",
    "details": [
      {
        "field": "taxIdentificationNumber",
        "message": "NIF no válido"
      }
    ]
  }
  ```

##### 2. Inicio de Sesión
- **URL**: `/api/v1/auth/login`
- **Método**: `POST`
- **Seguridad**:
  * Bloqueo tras 5 intentos fallidos
  * Registro de intentos de inicio de sesión

**Ejemplo de Solicitud**:
```json
{
  "email": "autonomo@ejemplo.com", 
  "password": "Fact_Pi_C3_2024!"
}
```

**Respuestas**:
- `200 OK`: Inicio de sesión correcto
  ```json
  {
    "accessToken": "jwt_token",
    "refreshToken": "refresh_token",
    "user": {
      "id": "abc123",
      "email": "autonomo@ejemplo.com",
      "role": "autonomo"
    },
    "expiresIn": 3600
  }
  ```
- `401 Unauthorized`: Credenciales inválidas
  ```json
  {
    "error": "Authentication Failed",
    "code": "INVALID_CREDENTIALS",
    "message": "Email o contraseña incorrectos"
  }
  ```

### 🔄 Flujo de Generación de Factura

#### Caso de Uso: Crear Nueva Factura
**Descripción**: Un usuario genera una factura para un cliente

**Pasos del Flujo**:
1. Usuario selecciona "Nueva Factura"
2. Introduce datos del cliente
3. Añade líneas de servicio/producto
4. Sistema calcula:
   - Base imponible
   - IVA
   - Retenciones (IRPF)
5. Genera PDF de factura
6. Permite envío por email
7. Registra factura en libro de facturas

**Reglas de Negocio**:
- Cumplimiento de facturación electrónica
- Numeración según serie de factura
- Cálculos fiscales automáticos

### 📊 Métricas de Caso de Uso

**Tiempos Objetivo**:
- Registro: < 30 segundos
- Generación de Factura: < 2 minutos
- Validación de Datos: < 500ms

**Casos Límite**:
- Usuarios sin conexión
- Facturas con múltiples impuestos
- Clientes internacionales
