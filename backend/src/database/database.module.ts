import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { databaseConfig } from '../config/database.config';

@Module({
  imports: [
    ConfigModule.forRoot({
      load: [databaseConfig],
      isGlobal: true,
    }),
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        ...configService.get('database'),
        
        // Hooks de eventos de conexión para logging
        subscribers: [],
        
        // Manejo de errores de conexión
        autoLoadEntities: true,
        
        // Configuraciones de depuración
        debug: process.env.NODE_ENV === 'development',
      }),
    }),
  ],
  exports: [TypeOrmModule],
})
export class DatabaseModule {
  // Método estático para configuración adicional si es necesario
  static register() {
    return {
      module: DatabaseModule,
      global: true,
    };
  }
}
