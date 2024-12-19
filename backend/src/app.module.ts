import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { dataSourceOptions } from '../ormconfig';

// Módulos de la aplicación
import { AuthModule } from './auth/auth.module';
import { UsuariosModule } from './usuarios/usuarios.module';
import { NotificacionesModule } from './notificaciones/notificaciones.module';
import { ModelosFiscalesModule } from './modelos-fiscales/modelos-fiscales.module';
import { EventosFiscalesModule } from './eventos-fiscales/eventos-fiscales.module';

@Module({
  imports: [
    // Configuración de variables de entorno
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '.env.development', '.env.production']
    }),

    // Configuración de base de datos
    TypeOrmModule.forRootAsync({
      useFactory: () => dataSourceOptions
    }),

    // Módulos de la aplicación
    AuthModule,
    UsuariosModule,
    NotificacionesModule,
    ModelosFiscalesModule,
    EventosFiscalesModule
  ],
  controllers: [],
  providers: []
})
export class AppModule {}
