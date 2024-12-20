import { MigrationInterface, QueryRunner } from "typeorm";

export class InitialSchema1701734400000 implements MigrationInterface {
    name = 'InitialSchema1701734400000'

    public async up(queryRunner: QueryRunner): Promise<void> {
        // Extensiones de PostgreSQL
        await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`);
        await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS "pgcrypto"`);

        // Crear tabla de usuarios
        await queryRunner.query(`
            CREATE TABLE "usuario" (
                "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                "email" VARCHAR(255) UNIQUE NOT NULL,
                "password" VARCHAR(255) NOT NULL,
                "nombre" VARCHAR(100) NOT NULL,
                "apellidos" VARCHAR(100),
                "rol" VARCHAR(50) NOT NULL DEFAULT 'usuario',
                "activo" BOOLEAN NOT NULL DEFAULT true,
                "ultimo_inicio_sesion" TIMESTAMP,
                "fecha_creacion" TIMESTAMP NOT NULL DEFAULT now(),
                "fecha_actualizacion" TIMESTAMP NOT NULL DEFAULT now()
            )
        `);

        // Crear tabla de clientes
        await queryRunner.query(`
            CREATE TABLE "cliente" (
                "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                "nombre" VARCHAR(100) NOT NULL,
                "apellidos" VARCHAR(100),
                "razon_social" VARCHAR(255),
                "nif" VARCHAR(20) UNIQUE NOT NULL,
                "email" VARCHAR(255),
                "telefono" VARCHAR(20),
                "direccion" VARCHAR(255),
                "codigo_postal" VARCHAR(10),
                "ciudad" VARCHAR(100),
                "provincia" VARCHAR(100),
                "pais" VARCHAR(100) DEFAULT 'España',
                "tipo_cliente" VARCHAR(50) NOT NULL DEFAULT 'particular',
                "activo" BOOLEAN NOT NULL DEFAULT true,
                "fecha_creacion" TIMESTAMP NOT NULL DEFAULT now(),
                "fecha_actualizacion" TIMESTAMP NOT DEFAULT now()
            )
        `);

        // Crear tabla de facturas
        await queryRunner.query(`
            CREATE TABLE "factura" (
                "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                "numero_factura" VARCHAR(50) UNIQUE NOT NULL,
                "cliente_id" uuid NOT NULL,
                "fecha_emision" TIMESTAMP NOT NULL DEFAULT now(),
                "fecha_vencimiento" TIMESTAMP NOT NULL,
                "base_imponible" DECIMAL(10,2) NOT NULL,
                "iva" DECIMAL(5,2) NOT NULL,
                "total" DECIMAL(10,2) NOT NULL,
                "estado" VARCHAR(50) NOT NULL DEFAULT 'pendiente',
                "notas" TEXT,
                "metodo_pago" VARCHAR(50) NOT NULL,
                "archivo_url" VARCHAR(255),
                FOREIGN KEY ("cliente_id") REFERENCES "cliente"("id") ON DELETE RESTRICT
            )
        `);

        // Crear tabla de líneas de factura
        await queryRunner.query(`
            CREATE TABLE "linea_factura" (
                "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
                "factura_id" uuid NOT NULL,
                "descripcion" VARCHAR(255) NOT NULL,
                "cantidad" DECIMAL(10,2) NOT NULL,
                "precio_unitario" DECIMAL(10,2) NOT NULL,
                "subtotal" DECIMAL(10,2) NOT NULL,
                "iva" DECIMAL(5,2) NOT NULL,
                "descuento" DECIMAL(5,2) DEFAULT 0,
                FOREIGN KEY ("factura_id") REFERENCES "factura"("id") ON DELETE CASCADE
            )
        `);

        // Crear índices para mejorar rendimiento
        await queryRunner.query(`
            CREATE INDEX "idx_usuario_email" ON "usuario" ("email");
            CREATE INDEX "idx_cliente_nif" ON "cliente" ("nif");
            CREATE INDEX "idx_factura_cliente" ON "factura" ("cliente_id");
            CREATE INDEX "idx_factura_estado" ON "factura" ("estado");
            CREATE INDEX "idx_linea_factura_factura" ON "linea_factura" ("factura_id");
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        // Eliminar índices
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_linea_factura_factura"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_factura_estado"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_factura_cliente"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_cliente_nif"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_usuario_email"`);

        // Eliminar tablas en orden inverso
        await queryRunner.query(`DROP TABLE IF EXISTS "linea_factura"`);
        await queryRunner.query(`DROP TABLE IF EXISTS "factura"`);
        await queryRunner.query(`DROP TABLE IF EXISTS "cliente"`);
        await queryRunner.query(`DROP TABLE IF EXISTS "usuario"`);

        // Eliminar extensiones
        await queryRunner.query(`DROP EXTENSION IF EXISTS "pgcrypto"`);
        await queryRunner.query(`DROP EXTENSION IF EXISTS "uuid-ossp"`);
    }
}
