const { DataSource } = require('typeorm');
const dotenv = require('dotenv');
const path = require('path');

// Cargar variables de entorno
dotenv.config({ path: path.resolve(__dirname, '.env') });

// Configuración de TypeORM
const dataSourceOptions = {
  type: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  username: process.env.DB_USERNAME || 'factupi',
  password: process.env.DB_PASSWORD || 'Fact_Pi_C3_2024!',
  database: process.env.DB_DATABASE || 'factupi_ce',
  
  // Configuración de entidades y migraciones
  entities: [
    path.join(__dirname, 'src/**/*.entity{.ts,.js}')
  ],
  migrations: [
    path.join(__dirname, 'src/database/migrations/*{.ts,.js}')
  ],

  // Configuraciones adicionales
  synchronize: process.env.NODE_ENV === 'development',
  logging: process.env.NODE_ENV === 'development',
  
  // Configuración SSL para producción
  ssl: process.env.NODE_ENV === 'production' ? { 
    rejectUnauthorized: false 
  } : false,

  migrationsTableName: 'migrations_history'
};

// Crear y exportar DataSource
const dataSource = new DataSource(dataSourceOptions);

// Método para conectar a la base de datos
const connectDatabase = async () => {
  try {
    await dataSource.initialize();
    console.log('✅ Conexión a base de datos establecida');
  } catch (error) {
    console.error('❌ Error conectando a base de datos:', error);
    process.exit(1);
  }
};

module.exports = {
  default: dataSource,
  dataSource,
  dataSourceOptions,
  connectDatabase
};
