import { DataSource, DataSourceOptions } from 'typeorm';
import { config } from 'dotenv';
import { join } from 'path';

// Cargar variables de entorno
config();

const isProduction = process.env.NODE_ENV === 'production';

// Configuración base de TypeORM
const baseConfig: DataSourceOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  
  // Entidades y migraciones
  entities: [join(__dirname, 'src/**/*.entity{.ts,.js}')],
  migrations: [join(__dirname, 'src/database/migrations/*{.ts,.js}')],
  
  // Configuraciones según entorno
  synchronize: !isProduction,
  logging: !isProduction,
  
  // Configuraciones de conexión
  connectTimeoutMS: 10000,
  maxQueryExecutionTime: 1000,
  poolSize: isProduction ? 50 : 10,
  
  // SSL para producción
  ssl: isProduction ? {
    rejectUnauthorized: false,
    ca: process.env.DB_SSL_CA,
  } : false,
  
  // Configuración de migraciones
  migrationsTableName: 'migrations_history',
  migrationsRun: true
};

// Crear DataSource
export const AppDataSource = new DataSource(baseConfig);

// Función de conexión mejorada
export const connectDatabase = async (): Promise<void> => {
  try {
    await AppDataSource.initialize();
    console.log('✅ Conexión a base de datos establecida');
    
    // Ejecutar migraciones pendientes
    const pendingMigrations = await AppDataSource.showMigrations();
    if (pendingMigrations) {
      console.log('🔄 Ejecutando migraciones pendientes...');
      await AppDataSource.runMigrations();
    }
  } catch (error) {
    console.error('❌ Error en la conexión a base de datos:', error);
    
    // Reintentar conexión en desarrollo
    if (!isProduction) {
      console.log('🔄 Reintentando conexión en 5 segundos...');
      setTimeout(connectDatabase, 5000);
      return;
    }
    
    process.exit(1);
  }
};

export default AppDataSource;
