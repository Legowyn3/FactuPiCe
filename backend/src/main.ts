import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as helmet from 'helmet';
import * as compression from 'compression';
import { AppModule } from './app.module';
import { connectDatabase } from '../ormconfig';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';

async function bootstrap() {
  // Inicializar aplicación NestJS
  const app = await NestFactory.create(AppModule, {
    logger: ['error', 'warn', 'log']
  });

  // Obtener servicio de configuración
  const configService = app.get(ConfigService);

  // Configuración de CORS
  app.enableCors({
    origin: configService.get('CORS_ORIGIN', '*'),
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization']
  });

  // Middleware de seguridad
  app.use(helmet());
  app.use(compression());

  // Configuración global de validación
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true
    })
  );

  // Filtros y interceptores globales
  app.useGlobalFilters(new AllExceptionsFilter());
  app.useGlobalInterceptors(new TransformInterceptor());

  // Prefijo global para rutas de API
  app.setGlobalPrefix('api/v1');

  // Conectar base de datos
  await connectDatabase();

  // Puerto de escucha
  const port = configService.get('PORT', 3000);
  await app.listen(port, () => {
    console.log(`🚀 Servidor corriendo en puerto ${port}`);
  });
}

bootstrap().catch(console.error);
