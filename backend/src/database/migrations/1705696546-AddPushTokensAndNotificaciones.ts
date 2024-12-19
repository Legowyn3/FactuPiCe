import { MigrationInterface, QueryRunner } from "typeorm";

export class AddPushTokensAndNotificaciones1705696546 implements MigrationInterface {
    name = 'AddPushTokensAndNotificaciones1705696546'

    public async up(queryRunner: QueryRunner): Promise<void> {
        // Agregar columna de push tokens a la tabla de usuarios
        await queryRunner.query(`ALTER TABLE "users" ADD "pushTokens" text array`);

        // Crear tabla de notificaciones
        await queryRunner.query(`
            CREATE TYPE "public"."notificacion_tipo_enum" AS ENUM('info', 'alerta', 'error', 'success');
            CREATE TYPE "public"."notificacion_canal_enum" AS ENUM('email', 'sms', 'push', 'in-app');
            
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

        // Eliminar tipos enum
        await queryRunner.query(`DROP TYPE "public"."notificacion_tipo_enum"`);
        await queryRunner.query(`DROP TYPE "public"."notificacion_canal_enum"`);

        // Eliminar columna de push tokens
        await queryRunner.query(`ALTER TABLE "users" DROP COLUMN "pushTokens"`);
    }
}
