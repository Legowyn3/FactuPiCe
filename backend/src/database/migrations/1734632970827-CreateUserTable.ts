import { MigrationInterface, QueryRunner } from "typeorm";

export class CreateUserTable1734632970827 implements MigrationInterface {
    name = 'CreateUserTable1734632970827'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`
            CREATE TYPE "public"."users_role_enum" AS ENUM('admin', 'freelance', 'empresa')
        `);
        await queryRunner.query(`
            CREATE TABLE "users" (
                "id" uuid NOT NULL DEFAULT uuid_generate_v4(),
                "email" character varying NOT NULL,
                "password" character varying NOT NULL,
                "role" "public"."users_role_enum" NOT NULL DEFAULT 'freelance',
                "isActive" boolean NOT NULL DEFAULT true,
                "refreshToken" character varying,
                "createdAt" TIMESTAMP NOT NULL DEFAULT now(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT now(),
                CONSTRAINT "UQ_97672ac88f789774dd47f7c8be3" UNIQUE ("email"),
                CONSTRAINT "PK_a3ffb1c0c8416b9fc6f907b7433" PRIMARY KEY ("id")
            )
        `);
        await queryRunner.query(`
            CREATE TYPE "public"."notificacion_tipo_enum" AS ENUM('info', 'alerta', 'error', 'success')
        `);
        await queryRunner.query(`
            CREATE TYPE "public"."notificacion_canal_enum" AS ENUM('email', 'sms', 'push', 'in-app')
        `);
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
                CONSTRAINT "PK_b4402a54386266ca21a86420f77" PRIMARY KEY ("id")
            )
        `);
        await queryRunner.query(`
            ALTER TABLE "notificacion"
            ADD CONSTRAINT "FK_acdc42b01f62aded0f2983100df" FOREIGN KEY ("usuarioId") REFERENCES "users"("id") ON DELETE NO ACTION ON UPDATE NO ACTION
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`
            ALTER TABLE "notificacion" DROP CONSTRAINT "FK_acdc42b01f62aded0f2983100df"
        `);
        await queryRunner.query(`
            DROP TABLE "notificacion"
        `);
        await queryRunner.query(`
            DROP TYPE "public"."notificacion_canal_enum"
        `);
        await queryRunner.query(`
            DROP TYPE "public"."notificacion_tipo_enum"
        `);
        await queryRunner.query(`
            DROP TABLE "users"
        `);
        await queryRunner.query(`
            DROP TYPE "public"."users_role_enum"
        `);
    }

}
