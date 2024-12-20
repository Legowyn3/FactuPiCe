import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import compression from 'compression';
import { connectDatabase } from './database/database.connection';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Conexión a base de datos
  await connectDatabase();

  // Configuración de CORS
  app.enableCors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    credentials: true,
  });

  // Middleware de seguridad
  app.use(helmet());

  // Compresión de respuestas
  app.use(compression());

  // Validación global de DTOs
  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,
    forbidNonWhitelisted: true,
    transform: true,
    transformOptions: {
      enableImplicitConversion: true,
    },
  }));

  // Configuración de Swagger
  const config = new DocumentBuilder()
    .setTitle('FactuPiCe API')
    .setDescription('API para la aplicación de facturación de autónomos')
    .setVersion('1.0')
    .addTag('clientes', 'Operaciones con clientes')
    .addTag('usuarios', 'Operaciones de usuarios')
    .addTag('autenticación', 'Endpoints de autenticación')
    .addBearerAuth()
    .build();
  
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api/docs', app, document, {
    customSiteTitle: 'FactuPiCe API Docs',
    customfavIcon: 'https://avatars.githubusercontent.com/u/YOUR_GITHUB_ID',
    customCss: `
      .swagger-ui .topbar { 
        background-color: #1976D2; 
      }
      .swagger-ui .topbar-wrapper img {
        content: url('https://your-logo-url');
        width: 50px;
        height: auto;
      }
    `
  });

  // Prefijo global para APIs
  app.setGlobalPrefix('api/v1');

  const port = process.env.PORT || 4000;
  await app.listen(port, () => {
    console.log(`🚀 Servidor corriendo en puerto ${port}`);
    console.log(`📄 Documentación de API disponible en: http://localhost:${port}/api/docs`);
  });
}
bootstrap();
