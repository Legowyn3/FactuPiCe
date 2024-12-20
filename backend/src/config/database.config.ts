import { registerAs } from '@nestjs/config';
import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import { DataSourceOptions } from 'typeorm';

export const databaseConfig = registerAs(
  'database',
  (): TypeOrmModuleOptions => ({
    type: 'postgres',
    host: process.env.DATABASE_HOST || 'localhost',
    port: parseInt(process.env.DATABASE_PORT || '5432', 10),
    username: process.env.DATABASE_USER || '',
    password: process.env.DATABASE_PASSWORD || '',
    database: process.env.DATABASE_NAME || '',
    
    // Configuraciones de sincronización y logging
    synchronize: process.env.DATABASE_SYNC === 'true',
    logging: process.env.DATABASE_LOGGING === 'true',
    
    // Configuraciones de migración
    migrationsTableName: 'migrations',
    migrations: ['src/migrations/**/*{.ts,.js}'],
    
    // Configuraciones de entidades
    autoLoadEntities: true,
    
    // Configuraciones de conexión
    connectTimeoutMS: 10000,
    maxQueryExecutionTime: 5000,
    
    // Configuraciones de pool de conexiones
    poolSize: 10,
    
    // Configuraciones de SSL (opcional)
    ssl: process.env.DATABASE_SSL === 'true' ? {
      rejectUnauthorized: false,
      ca: process.env.DATABASE_SSL_CA || '',
    } : false,
    
    // Extensiones de PostgreSQL
    extra: {
      statement_timeout: 5000, // Timeout de consultas en ms
      idle_in_transaction_session_timeout: 10000, // Timeout de transacciones inactivas
    },
  }),
);

export const connectionSource: DataSourceOptions = {
  type: 'postgres',
  host: process.env.DATABASE_HOST || 'localhost',
  port: parseInt(process.env.DATABASE_PORT || '5432', 10),
  username: process.env.DATABASE_USER || '',
  password: process.env.DATABASE_PASSWORD || '',
  database: process.env.DATABASE_NAME || '',
  
  // Configuraciones de migración
  migrationsTableName: 'migrations',
  migrations: ['src/migrations/**/*{.ts,.js}'],
  
  // Configuraciones de entidades
  entities: ['src/**/*.entity{.ts,.js}'],
};
