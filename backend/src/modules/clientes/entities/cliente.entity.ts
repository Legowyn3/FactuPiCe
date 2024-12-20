import { Entity, Column, PrimaryGeneratedColumn, OneToMany, BaseEntity } from 'typeorm';
import { Factura } from '../../facturas/entities/factura.entity';

@Entity('clientes')
export class Cliente extends BaseEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string | undefined;

  @Column()
  nombre: string | undefined;

  @Column()
  nif: string | undefined;

  @Column()
  email: string | undefined;

  @Column()
  telefono: string | undefined;

  @Column()
  direccion: string | undefined;

  @Column({ nullable: true })
  notas?: string;

  @OneToMany(() => Factura, factura => factura.cliente)
  facturas: Factura[] | undefined;
}