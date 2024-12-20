import { Entity, Column, ManyToOne, JoinColumn } from 'typeorm';
import { BaseEntity } from '../../../common/entities/base.entity';
import { Factura } from './factura.entity';

@Entity('lineas_factura')
export class LineaFactura extends BaseEntity {
  @ManyToOne(() => Factura, factura => factura.lineas, { nullable: false })
  @JoinColumn({ name: 'factura_id' })
  factura: Factura;

  @Column()
  descripcion: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  cantidad: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  precioUnitario: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  subtotal: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  iva: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  descuento: number;

  constructor(partial: Partial<LineaFactura> = {}) {
    super();
    Object.assign(this, {
      descuento: 0,
      ...partial
    });
  }
}
