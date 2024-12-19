-- Agregar columnas faltantes
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS apellidos VARCHAR;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono VARCHAR;
