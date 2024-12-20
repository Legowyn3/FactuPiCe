import { DataSource, DataSourceOptions } from 'typeorm';
import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';
import { config } from 'dotenv';
import { join } from 'path';

// Cargar variables de entorno
config();

const isProduction = process.env.NODE_ENV === 'production';

// Configuración base de TypeORM
export const dataSourceOptions: PostgresConnectionOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || '',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_DATABASE || '',
  
  // Entidades y migraciones
  entities: [join(__dirname, '../**/*.entity{.ts,.js}')],
  migrations: [join(__dirname, 'migrations/*{.ts,.js}')],
  
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
    ca: process.env.DB_SSL_CA || undefined,
  } : false,
  
  // Configuración de migraciones
  migrationsTableName: 'migrations_history',
  migrationsRun: true
};

// Crear DataSource
export const AppDataSource = new DataSource(dataSourceOptions);

// Función de conexión mejorada
export const connectDatabase = async (): Promise<void> => {
  try {
    await AppDataSource.initialize();
    console.log('✅ Conexión a base de datos establecida');
  } catch (error) {
    console.error('❌ Error al conectar a la base de datos:', error);
    process.exit(1);
  }
};

export default AppDataSource;
