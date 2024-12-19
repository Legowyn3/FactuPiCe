import { MigrationInterface, QueryRunner } from "typeorm";

export class InitialSchema1702928400000 implements MigrationInterface {
    name = 'InitialSchema1702928400000'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`
            CREATE TABLE "user" (
                "id" SERIAL PRIMARY KEY,
                "email" VARCHAR(255) UNIQUE NOT NULL,
                "password" VARCHAR(255) NOT NULL,
                "role" VARCHAR(50) NOT NULL,
                "pushToken" VARCHAR(255),
                "createdAt" TIMESTAMP DEFAULT now(),
                "updatedAt" TIMESTAMP DEFAULT now()
            )
        `);

        await queryRunner.query(`
            CREATE TABLE "notification" (
                "id" SERIAL PRIMARY KEY,
                "title" VARCHAR(255) NOT NULL,
                "content" TEXT NOT NULL,
                "type" VARCHAR(50) NOT NULL,
                "channel" VARCHAR(50) NOT NULL,
                "userId" INTEGER NOT NULL,
                "isRead" BOOLEAN DEFAULT false,
                "createdAt" TIMESTAMP DEFAULT now(),
                FOREIGN KEY ("userId") REFERENCES "user"("id") ON DELETE CASCADE
            )
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "notification"`);
        await queryRunner.query(`DROP TABLE "user"`);
    }
}
