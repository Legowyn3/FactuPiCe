import { MigrationInterface, QueryRunner } from "typeorm";

export class InitialSchema1705696546 implements MigrationInterface {
    name = 'InitialSchema1705696546'

    public async up(queryRunner: QueryRunner): Promise<void> {
        // Crear extensión para UUID
        await queryRunner.query(`CREATE EXTENSION IF NOT EXISTS "uuid-ossp"`);

        // Crear enum para roles de usuario
        await queryRunner.query(`
            CREATE TYPE "public"."user_role_enum" AS ENUM('admin', 'freelance', 'empresa')
        `);

        // Crear tabla de usuarios
        await queryRunner.query(`
            CREATE TABLE "users" (
                "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
                "email" character varying NOT NULL,
                "password" character varying NOT NULL,
                "role" "public"."user_role_enum" NOT NULL DEFAULT 'freelance',
                "isActive" boolean NOT NULL DEFAULT true,
                "refreshToken" character varying,
                "pushTokens" text array,
                "createdAt" TIMESTAMP NOT NULL DEFAULT now(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT now(),
                CONSTRAINT "UQ_97672ac88f5fcbe72b8fff2c7a9" UNIQUE ("email"),
                CONSTRAINT "PK_a3ffb1c0c8416b9fc6f907b7ed8" PRIMARY KEY ("id")
            )
        `);

        // Crear enums para notificaciones
        await queryRunner.query(`
            CREATE TYPE "public"."notificacion_tipo_enum" AS ENUM('info', 'alerta', 'error', 'success')
        `);
        await queryRunner.query(`
            CREATE TYPE "public"."notificacion_canal_enum" AS ENUM('email', 'sms', 'push', 'in-app')
        `);

        // Crear tabla de notificaciones
        await queryRunner.query(`
            CREATE TABLE "notificacion" (
                "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
                "titulo" character varying NOT NULL,
                "contenido" text NOT NULL,
                "tipo" "public"."notificacion_tipo_enum" NOT NULL DEFAULT 'info',
                "canal" "public"."notificacion_canal_enum" NOT NULL DEFAULT 'in-app',
                "usuarioId" uuid NOT NULL,
                "leida" boolean NOT NULL DEFAULT false,
                "fechaCreacion" TIMESTAMP NOT NULL DEFAULT now(),
                CONSTRAINT "PK_notificacion_id" PRIMARY KEY ("id")
            )
        `);

        // Agregar foreign key de usuario a notificaciones
        await queryRunner.query(`
            ALTER TABLE "notificacion" 
            ADD CONSTRAINT "FK_notificacion_usuario" 
            FOREIGN KEY ("usuarioId") 
            REFERENCES "users"("id") 
            ON DELETE CASCADE 
            ON UPDATE NO ACTION
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        // Eliminar foreign key
        await queryRunner.query(`ALTER TABLE "notificacion" DROP CONSTRAINT "FK_notificacion_usuario"`);

        // Eliminar tabla de notificaciones
        await queryRunner.query(`DROP TABLE "notificacion"`);

        // Eliminar tipos enum de notificaciones
        await queryRunner.query(`DROP TYPE "public"."notificacion_tipo_enum"`);
        await queryRunner.query(`DROP TYPE "public"."notificacion_canal_enum"`);

        // Eliminar tabla de usuarios
        await queryRunner.query(`DROP TABLE "users"`);

        // Eliminar tipo enum de roles
        await queryRunner.query(`DROP TYPE "public"."user_role_enum"`);

        // Eliminar extensión UUID
        await queryRunner.query(`DROP EXTENSION "uuid-ossp"`);
    }
}
