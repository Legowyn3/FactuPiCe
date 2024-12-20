# Etapa de construcción
FROM node:20-alpine AS builder

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY tsconfig*.json ./

# Instalar dependencias con cache limpio
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Construir la aplicación
RUN npm run build

# Etapa de producción
FROM node:20-alpine AS production

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copiar dependencias y build desde la etapa anterior
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# Copiar archivos de configuración
COPY --from=builder /app/.env.production ./.env
COPY --from=builder /app/ormconfig.js ./

# Cambiar al usuario no root
USER appuser

# Variables de entorno
ENV NODE_ENV=production \
    PORT=3000 \
    RATE_LIMIT_WINDOW="15m" \
    RATE_LIMIT_MAX_REQUESTS=100

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["npm", "run", "start:prod"]
