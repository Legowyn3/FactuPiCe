import { Entity, Column, ManyToOne, OneToMany, JoinColumn } from 'typeorm';
import { BaseEntity } from '../../../common/entities/base.entity';
import { Cliente } from '../../clientes/entities/cliente.entity';
import { LineaFactura } from './linea-factura.entity';

@Entity('facturas')
export class Factura extends BaseEntity {
  @Column({ unique: true })
  numeroFactura: string = '';

  @ManyToOne(() => Cliente, { nullable: false })
  @JoinColumn({ name: 'cliente_id' })
  cliente: Cliente = {} as Cliente;

  @Column({ type: 'uuid', name: 'cliente_id' })
  clienteId: string = '';

  @Column({ type: 'date' })
  fechaEmision: Date = new Date();

  @Column({ type: 'date' })
  fechaVencimiento: Date = new Date();

  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  baseImponible: number = 0;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  iva: number = 0;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  retencion: number = 0;

  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  total: number = 0;

  @OneToMany(() => LineaFactura, linea => linea.factura, { cascade: true })
  lineas: LineaFactura[] = [];

  @Column({ 
    type: 'enum', 
    enum: ['pendiente', 'pagada', 'anulada'], 
    default: 'pendiente' 
  })
  estado: 'pendiente' | 'pagada' | 'anulada' = 'pendiente';

  @Column({ nullable: true })
  notas: string = '';

  constructor(partial: Partial<Factura> = {}) {
    super();
    Object.assign(this, {
      numeroFactura: '',
      cliente: {} as Cliente,
      clienteId: '',
      fechaEmision: new Date(),
      fechaVencimiento: new Date(),
      baseImponible: 0,
      iva: 0,
      retencion: 0,
      total: 0,
      lineas: [],
      estado: 'pendiente',
      notas: '',
      ...partial
    });
  }
}