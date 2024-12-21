# Módulo de Autenticación FactuPiCe

## Características de Seguridad

### Autenticación
- Inicio de sesión con JWT
- Tokens de acceso y refresco
- Estrategias de autenticación local y JWT

### Multi-Factor Authentication (MFA)
- Generación de secretos TOTP
- Configuración de MFA mediante QR Code
- Verificación de tokens de un solo uso

### Políticas de Seguridad
- Bloqueo de cuenta tras múltiples intentos fallidos
- Control de estado de cuenta (activo/bloqueado)
- Registro de intentos de inicio de sesión

## Endpoints

### Autenticación
- `POST /auth/login`: Iniciar sesión
- `POST /auth/refresh`: Refrescar tokens
- `POST /auth/logout`: Cerrar sesión

### MFA
- `POST /auth/mfa/setup`: Configurar MFA
- `POST /auth/mfa/verify`: Verificar token MFA

### Seguridad
- `GET /auth/security/status/:userId`: Verificar estado de cuenta

## Configuración

### Variables de Entorno
- `JWT_SECRET`: Clave secreta para tokens
- `MAX_LOGIN_ATTEMPTS`: Número máximo de intentos de inicio de sesión
- `ACCOUNT_LOCK_DURATION`: Duración del bloqueo de cuenta

## Mejores Prácticas
- Tokens de corta duración
- Rotación periódica de credenciales
- Almacenamiento seguro de tokens
- Validaciones estrictas

## Próximas Mejoras
- Integración con proveedores de identidad externos
- Soporte para autenticación de dos factores más robusta
- Registro de auditoría de eventos de seguridad
