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
      ...partial
    });
  }
} 