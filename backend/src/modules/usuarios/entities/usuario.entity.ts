import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { Exclude } from 'class-transformer';

@Entity('usuarios')
export class Usuario {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column()
  nombre: string = '';

  @Column({ unique: true })
  email: string = '';

  @Column()
  @Exclude()
  password: string = '';

  @Column({ nullable: true })
  @Exclude()
  refreshToken?: string;

  @Column({ default: false })
  mfaEnabled: boolean;

  @Column({ nullable: true })
  @Exclude()
  mfaSecret?: string;

  @Column({ default: 0 })
  failedLoginAttempts: number;

  @Column({ default: false })
  isLocked: boolean;

  @Column({ nullable: true })
  lockedUntil?: Date;

  @Column({ nullable: true })
  lastLoginAttempt?: Date;

  @Column({ nullable: true })
  lastPasswordChangeAt?: Date;

  @Column({ default: true })
  isActive: boolean;

  @Column({ nullable: true })
  passwordResetToken?: string;

  @Column({ nullable: true })
  passwordResetExpires?: Date;

  @Column({ nullable: true })
  nif: string = '';

  @Column({ nullable: true })
  direccion: string = '';

  @Column({ nullable: true })
  telefono: string = '';

  @Column({ nullable: true })
  logo?: string = '';

  @Column({ default: true })
  activo: boolean = true;

  @CreateDateColumn()
  createdAt: Date = new Date();

  @UpdateDateColumn()
  updatedAt: Date = new Date();

  constructor(partial: Partial<Usuario> = {}) {
    Object.assign(this, {
      nombre: '',
      email: '',
      password: '',
      nif: '',
      direccion: '',
      telefono: '',
      logo: '',
      activo: true,
      createdAt: new Date(),
      updatedAt: new Date(),
      refreshToken: undefined,
      mfaEnabled: false,
      mfaSecret: undefined,
      failedLoginAttempts: 0,
      isLocked: false,
      lockedUntil: undefined,
      lastLoginAttempt: undefined,
      lastPasswordChangeAt: undefined,
      isActive: true,
      passwordResetToken: undefined,
      passwordResetExpires: undefined,
      ...partial
    });
  }
}