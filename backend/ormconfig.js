const { DataSource } = require('typeorm');
const dotenv = require('dotenv');
const path = require('path');

// Cargar variables de entorno
dotenv.config({ path: path.resolve(__dirname, '.env') });

const dataSourceOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || 'factupi',
  password: process.env.DB_PASSWORD || 'Fact_Pi_C3_2024!',
  database: process.env.DB_DATABASE || 'factupi_ce',
  
  entities: [path.resolve(__dirname, 'src/**/*.entity{.ts,.js}')],
  migrations: [path.resolve(__dirname, 'src/database/migrations/**/*{.ts,.js}')],
  
  migrationsTableName: 'migrations_history',
  synchronize: false,
  logging: true
};

const dataSource = new DataSource(dataSourceOptions);

module.exports = {
  ...dataSourceOptions,
  dataSource
};
