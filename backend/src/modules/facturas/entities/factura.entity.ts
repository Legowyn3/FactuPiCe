import { Entity, Column, ManyToOne, OneToMany, JoinColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { BaseEntity } from '../../../common/entities/base.entity';
import { Cliente } from '../../clientes/entities/cliente.entity';
import { LineaFactura } from './linea-factura.entity';
import { IsNotEmpty, IsPositive, Min, Max } from 'class-validator';

export enum EstadoFactura {
  PENDIENTE = 'pendiente',
  PAGADA = 'pagada',
  ANULADA = 'anulada',
  PARCIAL = 'parcial'
}

@Entity('facturas')
export class Factura extends BaseEntity {
  @Column({ unique: true })
  @IsNotEmpty({ message: 'El número de factura no puede estar vacío' })
  numeroFactura!: string;

  @ManyToOne(() => Cliente, { nullable: false })
  @JoinColumn({ name: 'cliente_id' })
  cliente!: Cliente;

  @Column({ type: 'uuid', name: 'cliente_id' })
  clienteId!: string;

  @Column({ type: 'date' })
  @IsNotEmpty({ message: 'La fecha de emisión es obligatoria' })
  fechaEmision!: Date;

  @Column({ type: 'date' })
  @IsNotEmpty({ message: 'La fecha de vencimiento es obligatoria' })
  fechaVencimiento!: Date;

  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  @IsPositive({ message: 'La base imponible debe ser un número positivo' })
  baseImponible!: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  @Min(0, { message: 'El IVA no puede ser negativo' })
  @Max(100, { message: 'El IVA no puede ser mayor al 100%' })
  iva!: number;

  @Column({ type: 'decimal', precision: 5, scale: 2, default: 0 })
  @Min(0, { message: 'La retención no puede ser negativa' })
  @Max(100, { message: 'La retención no puede ser mayor al 100%' })
  retencion!: number;

  @Column({ type: 'decimal', precision: 10, scale: 2, default: 0 })
  @IsPositive({ message: 'El total debe ser un número positivo' })
  total!: number;

  @OneToMany(() => LineaFactura, linea => linea.factura, { cascade: true })
  lineas!: LineaFactura[];

  @Column({ 
    type: 'enum', 
    enum: EstadoFactura, 
    default: EstadoFactura.PENDIENTE 
  })
  estado!: EstadoFactura;

  @Column({ nullable: true })
  notas?: string;

  @CreateDateColumn()
  createdAt!: Date;

  @UpdateDateColumn()
  updatedAt!: Date;

  constructor(partial: Partial<Factura> = {}) {
    super();
    if (partial) {
      Object.assign(this, {
        numeroFactura: partial.numeroFactura || '',
        cliente: partial.cliente || {} as Cliente,
        clienteId: partial.clienteId || '',
        fechaEmision: partial.fechaEmision || new Date(),
        fechaVencimiento: partial.fechaVencimiento || new Date(),
        baseImponible: partial.baseImponible || 0,
        iva: partial.iva || 0,
        retencion: partial.retencion || 0,
        total: partial.total || 0,
        lineas: partial.lineas || [],
        estado: partial.estado || EstadoFactura.PENDIENTE,
        notas: partial.notas || '',
        createdAt: partial.createdAt || new Date(),
        updatedAt: partial.updatedAt || new Date()
      });
    }
  }

  // Método para calcular totales
  calcularTotales() {
    // Calcular base imponible sumando las líneas de factura
    this.baseImponible = this.lineas.reduce(
      (total, linea) => total + (linea.cantidad * linea.precioUnitario), 
      0
    );

    // Calcular IVA
    const importeIva = this.baseImponible * (this.iva / 100);

    // Calcular retención
    const importeRetencion = this.baseImponible * (this.retencion / 100);

    // Calcular total
    this.total = this.baseImponible + importeIva - importeRetencion;
  }
}