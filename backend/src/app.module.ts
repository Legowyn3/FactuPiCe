import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import AppDataSource from '../typeorm.config';

// Módulos de la aplicación
import { AuthModule } from './modules/auth/auth.module';
import { UsuariosModule } from './modules/usuarios/usuarios.module';
import { NotificacionesModule } from './notificaciones/notificaciones.module';
import { ClientesModule } from './modules/clientes/clientes.module';

@Module({
  imports: [
    // Configuración de variables de entorno
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '.env.development', '.env.production']
    }),

    // Configuración de base de datos
    TypeOrmModule.forRootAsync({
      useFactory: () => AppDataSource.options
    }),

    // Módulos de la aplicación
    AuthModule,
    UsuariosModule,
    NotificacionesModule,
    ClientesModule
  ],
  controllers: [],
  providers: []
})
export class AppModule {}
