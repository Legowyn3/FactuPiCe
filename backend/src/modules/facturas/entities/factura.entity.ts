import { Entity, Column, PrimaryGeneratedColumn, ManyToOne, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { Cliente } from '../../clientes/entities/cliente.entity';
import { ConceptoFactura } from './concepto-factura.entity';

export enum EstadoFactura {
  BORRADOR = 'BORRADOR',
  EMITIDA = 'EMITIDA',
  PAGADA = 'PAGADA',
  ANULADA = 'ANULADA'
}

@Entity('facturas')
export class Factura {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  numero: string;

  @Column({ type: 'date' })
  fecha: Date;

  @ManyToOne(() => Cliente, cliente => cliente.facturas)
  cliente: Cliente;

  @Column()
  clienteId: string;

  @OneToMany(() => ConceptoFactura, concepto => concepto.factura, {
    cascade: true,
    eager: true
  })
  conceptos: ConceptoFactura[];

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  subtotal: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  iva: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  retencion: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  total: number;

  @Column({
    type: 'enum',
    enum: EstadoFactura,
    default: EstadoFactura.BORRADOR
  })
  estado: EstadoFactura;

  @Column({ type: 'text', nullable: true })
  observaciones?: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
} 