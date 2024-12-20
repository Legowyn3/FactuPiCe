import { Entity, Column, ManyToOne, JoinColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { BaseEntity } from '../../../common/entities/base.entity';
import { Factura } from './factura.entity';
import { IsNotEmpty, IsPositive, Min, Max } from 'class-validator';

@Entity('lineas_factura')
export class LineaFactura extends BaseEntity {
  @ManyToOne(() => Factura, factura => factura.lineas, { nullable: false })
  @JoinColumn({ name: 'factura_id' })
  factura!: Factura;

  @Column()
  @IsNotEmpty({ message: 'La descripción de la línea no puede estar vacía' })
  descripcion!: string;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  @IsPositive({ message: 'La cantidad debe ser un número positivo' })
  cantidad!: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  @IsPositive({ message: 'El precio unitario debe ser un número positivo' })
  precioUnitario!: number;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  @IsPositive({ message: 'El subtotal debe ser un número positivo' })
  subtotal!: number;

  @Column({ type: 'decimal', precision: 5, scale: 2 })
  @Min(0, { message: 'El IVA no puede ser negativo' })
  @Max(100, { message: 'El IVA no puede ser mayor al 100%' })
  iva!: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  @Min(0, { message: 'El descuento no puede ser negativo' })
  @Max(100, { message: 'El descuento no puede ser mayor al 100%' })
  descuento!: number;

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;

  constructor(partial: Partial<LineaFactura> = {}) {
    super();
    if (partial) {
      Object.assign(this, {
        descripcion: partial.descripcion || '',
        cantidad: partial.cantidad || 0,
        precioUnitario: partial.precioUnitario || 0,
        subtotal: partial.subtotal || 0,
        iva: partial.iva || 0,
        descuento: partial.descuento || 0,
        createdAt: partial.createdAt || new Date(),
        updatedAt: partial.updatedAt || new Date(),
        factura: partial.factura || {} as Factura
      });
    }
  }

  // Método para calcular el subtotal
  calcularSubtotal() {
    this.subtotal = this.cantidad * this.precioUnitario;
    return this.subtotal;
  }

  // Método para aplicar descuento
  aplicarDescuento(porcentajeDescuento: number) {
    if (porcentajeDescuento < 0 || porcentajeDescuento > 100) {
      throw new Error('El descuento debe estar entre 0 y 100');
    }
    this.descuento = porcentajeDescuento;
    const descuentoImporte = this.subtotal * (porcentajeDescuento / 100);
    return this.subtotal - descuentoImporte;
  }
}
