# FactuPiCe: Sistema de Facturación para Autónomos y Empresas

## Información del Proyecto
- **Versión:** 0.2.0
- **Estado:** En desarrollo activo
- **Última actualización:** 2024-12-20
- **Repositorio:** [GitHub - FactuPiCe](https://github.com/Legowyn3/FactuPiCe)

## Configuración del Repositorio

### Repositorio GitHub
- **Nombre**: FactuPiCe
- **URL**: https://github.com/Legowyn3/FactuPiCe
- **Tipo**: Repositorio Público
- **Rama Principal**: main

### Ubicación Local
- **Directorio de Trabajo**: `/home/piqueras/Documentos/FactuPiCeNew`

### Instrucciones de Backup
Para realizar una copia de seguridad o clonar el proyecto:
1. Clonar repositorio: 
   ```bash
   git clone https://github.com/Legowyn3/FactuPiCe.git
   ```
2. Cambiar a la rama principal:
   ```bash
   git checkout main
   ```

## Descripción General
FactuPiCe es una aplicación de facturación diseñada específicamente para autónomos y empresas en España, cumpliendo con las regulaciones fiscales españolas.

## Arquitectura del Sistema

### Diagrama de Alto Nivel
```
[Frontend] <--> [Backend API] <--> [Base de Datos PostgreSQL]
                    |
                    +--> [Servicios Externos]
                    |
                    +--> [Monitoreo Prometheus]
```

### Componentes Principales
- **Frontend:** En definición (potencial framework: React, Vue)
- **Backend:** NestJS con TypeScript
- **Base de Datos:** PostgreSQL
- **Autenticación:** JWT con Passport.js
- **Monitoreo:** Prometheus
- **Contenedorización:** Docker (opcional)

## Tecnologías Principales

### Backend
- Lenguaje: TypeScript 4.9+
- Framework: NestJS 9.x
- ORM: TypeORM 0.3.x
- Base de Datos: PostgreSQL 13+

### Autenticación y Seguridad
- JWT (JSON Web Tokens)
- Passport.js
- bcrypt para encriptación
- Validación de entrada de datos

### Infraestructura
- Contenedores: Docker
- Orquestación: Pendiente
- CI/CD: Configuración inicial

## Estrategia de Seguridad

### Principios
- Encriptación de contraseñas con bcrypt
- Validación de tokens en cada solicitud
- Protección de datos sensibles
- Validación estricta de entrada de datos

### Políticas de Seguridad
- Rotación periódica de credenciales
- Gestión de secretos
- Configuración de CORS
- Validación de entrada de datos
- Logging de eventos de seguridad

## Estado de Desarrollo

### Características Implementadas
#### Seguridad
- [x] Autenticación JWT
- [x] Validación de contraseñas
- [x] Middleware de seguridad
- [ ] Multi-Factor Authentication (MFA)

#### Modelo de Datos
- [x] Modelo de Factura
- [x] Modelo de Cliente
- [x] Configuración inicial de base de datos
- [ ] Validaciones de negocio

#### Facturación
- [ ] Generación de facturas
- [ ] Cálculo automático de IVA
- [ ] Exportación a PDF
- [ ] Integración con formatos fiscales

#### Monitoreo
- [x] Integración de Prometheus
- [x] Métricas personalizadas
- [ ] Dashboard de monitoreo
- [ ] Alertas y notificaciones

## Próximos Pasos

### Curto Plazo (Q1 2024)
1. Completar implementación de autenticación
2. Desarrollar lógica de generación de facturas
3. Implementar validaciones de negocio
4. Configurar exportación a formatos fiscales

### Medio Plazo (Q2 2024)
1. Integración con servicios externos
2. Definir estrategia de frontend
3. Implementar pruebas de integración
4. Configurar CI/CD

### Largo Plazo (Q3-Q4 2024)
1. Soporte para múltiples idiomas
2. Integración con pasarelas de pago
3. Reporting avanzado
4. Optimización de rendimiento

## Documentación Técnica

### Configuración de Desarrollo

#### Requisitos Previos
- Node.js 18.x
- npm 9.x
- PostgreSQL 13+
- Docker (opcional)

#### Scripts de NPM
- `npm run start`: Iniciar servidor en modo desarrollo
- `npm run build`: Compilar proyecto
- `npm run migration:create`: Crear nueva migración
- `npm run migration:generate`: Generar archivos de migración
- `npm run test`: Ejecutar pruebas unitarias

### Guía de Configuración Inicial
1. Clonar repositorio
2. Instalar dependencias: `npm install`
3. Configurar variables de entorno
4. Inicializar base de datos
5. Ejecutar migraciones
6. Iniciar servidor de desarrollo

## Métricas y Monitoreo

### Métricas Técnicas
- **Cobertura de pruebas:** Por definir
- **Tiempo de respuesta del API:** Por medir
- **Complejidad ciclomática:** Por evaluar

### Monitoreo Planificado
- Métricas de rendimiento
- Logs de aplicación
- Seguimiento de errores
- Alertas de sistema

## Contribución

### Guía para Desarrolladores
1. Fork del repositorio
2. Crear rama feature/fix
3. Seguir guía de estilo de código
4. Pasar tests de CI
5. Crear Pull Request
6. Revisión de código

### Estándares de Código
- TypeScript con strict mode
- Seguir guía de estilo de NestJS
- Documentación de código
- Cobertura de tests

## Contacto y Soporte
- Mantenedor: [Tu nombre]
- Email: [Tu email]
- Reportar issues: [Enlace a GitHub Issues]

## Licencia
[Especificar licencia del proyecto]

## Gestión de Proyecto
- Metodología: Scrum adaptado
- Herramientas: GitHub Projects
- Frecuencia de sprints: Quincenal
- Revisiones técnicas: Semanales

## Cumplimiento Normativo
- Normativas fiscales españolas
- LOPD
- Facturación electrónica
- Próxima certificación: [Detalles]

## Apéndices
- [Enlace a documentación detallada]
- [Guía de instalación]
- [Especificación de API]

## Lanzamiento y Roadmap Detallado

### Estimación de Lanzamiento

#### Base Estable (MVP - Producto Mínimo Viable)
- **Fecha Estimada:** Q3 2024 (Septiembre-Octubre)
- **Estado Actual:** En desarrollo

##### Criterios para Base Estable
Funcionalidades Críticas:
- [x] Autenticación de usuarios
- [x] Modelo de datos de facturas
- [x] Configuración de base de datos
- [ ] Generación básica de facturas
- [ ] Cálculo de IVA
- [ ] Exportación a PDF
- [ ] Validaciones de negocio
- [ ] Pruebas unitarias e integración
- [ ] Configuración de CI/CD
- [ ] Monitoreo básico

#### Beta Pública
- **Fecha Estimada:** Q4 2024 (Noviembre-Diciembre)

##### Criterios para Beta Pública
- Todas las funcionalidades del MVP completadas
- Integración con servicios fiscales básicos
- Interfaz de usuario funcional
- Documentación completa
- Soporte inicial implementado
- Pruebas de seguridad realizadas
- Cumplimiento inicial de normativas fiscales

### Plan de Desarrollo Detallado

#### Próximos Pasos Inmediatos
1. **Modelo de Datos y Entidades**
   - Completar modelos de Factura, Cliente, Línea de Factura
   - Implementar validaciones de negocio
   - Definir relaciones entre entidades

2. **Lógica de Negocio**
   - Desarrollar servicio de generación de facturas
   - Implementar cálculo de IVA
   - Crear servicio de exportación a PDF
   - Definir reglas de negocio específicas

3. **Infraestructura y Configuración**
   - Configurar CI/CD (GitHub Actions)
   - Implementar pipeline de testing
   - Configurar monitoreo con Prometheus
   - Definir estrategia de logging

4. **Seguridad**
   - Completar implementación de JWT
   - Añadir Multi-Factor Authentication
   - Realizar auditoría de seguridad inicial
   - Implementar rate limiting

5. **Integración Fiscal**
   - Investigar requisitos de TicketBAI
   - Definir estrategia de cumplimiento normativo
   - Preparar integración con servicios de la AEAT

### Inversión y Recursos

#### Estimación de Recursos
- **Equipo:** 2-3 desarrolladores
- **Duración Estimada:** 
  - Hasta MVP: 3-4 meses
  - Hasta Beta Pública: 5-6 meses
- **Costes Estimados:** 30,000€ - 50,000€

#### Factores Clave de Éxito
- Desarrollo iterativo
- Comunicación clara
- Priorización de features
- Flexibilidad en el scope

### Riesgos y Mitigación

#### Posibles Desafíos
1. Complejidad de integración fiscal
2. Requisitos de seguridad cambiantes
3. Pruebas exhaustivas
4. Cambios en regulaciones

#### Estrategias de Mitigación
- Consulta con asesor fiscal
- Revisiones de seguridad frecuentes
- Desarrollo modular
- Documentación detallada
- Comunicación proactiva con stakeholders

### Métricas de Progreso
- Cobertura de tests
- Tiempo de desarrollo de features
- Número de bugs encontrados
- Cumplimiento de requisitos normativos

### Próxima Revisión
- **Fecha:** Enero 2024
- **Objetivo:** Validar progreso del MVP
- **Participantes:** Equipo de desarrollo, stakeholders

## Últimas Mejoras y Desarrollo

### Versión 0.2.0 (2024-12-20)

#### Módulo de Líneas de Factura
- **Entidades**:
  - Actualización del modelo `LineaFactura` con validaciones robustas
  - Añadidos campos de auditoría (`createdAt`, `updatedAt`)
  - Implementados métodos de negocio:
    - `calcularSubtotal()`: Cálculo automático del subtotal
    - `aplicarDescuento()`: Aplicación de descuentos con validaciones

- **DTOs (Data Transfer Objects)**:
  - Creados `CreateLineaFacturaDto` y `UpdateLineaFacturaDto`
  - Implementadas validaciones con `class-validator`
  - Documentación de propiedades con Swagger

- **Servicio**:
  - Implementado `LineaFacturaService` con operaciones CRUD completas
  - Mejora del manejo de errores con tipado explícito
  - Gestión de relaciones entre líneas de factura y facturas
  - Cálculo automático de totales

- **Controlador**:
  - Creado `LineaFacturaController` con endpoints REST
  - Protección de endpoints con JWT
  - Documentación de API con Swagger

#### Mejoras de Desarrollo
- Resolución de errores de TypeScript en modelos y DTOs
- Implementación de validaciones de negocio
- Mejora de la gestión de errores
- Añadidos campos de auditoría en entidades

#### Próximos Pasos
- Implementar pruebas unitarias para el módulo de líneas de factura
- Configurar módulo de facturas
- Revisar y optimizar configuraciones de validación

### Control de Versiones y Documentación
- **Política de Documentación**: Actualizar `PROJECT_SUMMARY.md` después de cada iteración de desarrollo
- **Política de Respaldo**: Realizar commits y push a GitHub después de cada conjunto significativo de cambios

### Notas Importantes
- Mantener siempre actualizada la documentación del proyecto
- Realizar commits frecuentes con descripciones claras
- Priorizar la calidad del código y las validaciones de negocio

*Última actualización: 2024-12-20*
