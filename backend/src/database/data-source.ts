import { DataSource, DataSourceOptions } from 'typeorm';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Cargar variables de entorno
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const dataSourceOptions: DataSourceOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || 'factupi',
  password: process.env.DB_PASSWORD || 'Fact_Pi_C3_2024!',
  database: process.env.DB_DATABASE || 'factupi_ce',
  
  // Configuración de entidades y migraciones
  entities: [
    path.join(__dirname, '../**/*.entity{.ts,.js}')
  ],
  migrations: [
    path.join(__dirname, 'migrations/*{.ts,.js}')
  ],

  // Configuraciones adicionales
  synchronize: false,
  logging: true,
  
  // Configuración SSL para producción
  ssl: process.env.NODE_ENV === 'production' ? { 
    rejectUnauthorized: false 
  } : false
};

// Exportar única instancia de DataSource
export default new DataSource(dataSourceOptions);
