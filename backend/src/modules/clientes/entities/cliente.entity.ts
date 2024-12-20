import { Entity, Column, PrimaryGeneratedColumn, OneToMany, CreateDateColumn, UpdateDateColumn, DeleteDateColumn } from 'typeorm';
import { Factura } from '../../facturas/entities/factura.entity';
import { IsEmail, IsNotEmpty, IsOptional, Length } from 'class-validator';

@Entity('clientes')
export class Cliente {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column()
  @IsNotEmpty({ message: 'El nombre del cliente no puede estar vacío' })
  @Length(2, 100, { message: 'El nombre debe tener entre 2 y 100 caracteres' })
  nombre!: string;

  @Column({ unique: true })
  @IsNotEmpty({ message: 'El NIF/CIF no puede estar vacío' })
  @Length(9, 9, { message: 'El NIF/CIF debe tener 9 caracteres' })
  nif!: string;

  @Column()
  @IsEmail({}, { message: 'Formato de email inválido' })
  email!: string;

  @Column()
  @IsNotEmpty({ message: 'El teléfono no puede estar vacío' })
  @Length(9, 15, { message: 'El teléfono debe tener entre 9 y 15 caracteres' })
  telefono!: string;

  @Column()
  @IsNotEmpty({ message: 'La dirección no puede estar vacía' })
  @Length(5, 200, { message: 'La dirección debe tener entre 5 y 200 caracteres' })
  direccion!: string;

  @Column({ nullable: true })
  @IsOptional()
  notas?: string;

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;

  @DeleteDateColumn()
  deletedAt?: Date;

  @OneToMany(() => Factura, factura => factura.cliente)
  facturas!: Factura[];

  constructor(partial: Partial<Cliente> = {}) {
    if (partial) {
      Object.assign(this, {
        id: partial.id || '',
        nombre: partial.nombre || '',
        nif: partial.nif || '',
        email: partial.email || '',
        telefono: partial.telefono || '',
        direccion: partial.direccion || '',
        notas: partial.notas || '',
        createdAt: partial.createdAt || new Date(),
        updatedAt: partial.updatedAt || new Date(),
        facturas: partial.facturas || []
      });
    }
  }
}