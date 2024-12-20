import { IsNotEmpty, IsPositive, Min, Max, IsOptional, IsUUID } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateLineaFacturaDto {
  @ApiProperty({ 
    description: 'Descripción de la línea de factura', 
    example: 'Servicio de consultoría' 
  })
  @IsNotEmpty({ message: 'La descripción de la línea no puede estar vacía' })
  descripcion!: string;

  @ApiProperty({ 
    description: 'Cantidad del producto o servicio', 
    example: 2 
  })
  @IsPositive({ message: 'La cantidad debe ser un número positivo' })
  cantidad!: number;

  @ApiProperty({ 
    description: 'Precio unitario del producto o servicio', 
    example: 100.50 
  })
  @IsPositive({ message: 'El precio unitario debe ser un número positivo' })
  precioUnitario!: number;

  @ApiPropertyOptional({ 
    description: 'Porcentaje de IVA aplicable', 
    example: 21,
    default: 0 
  })
  @IsOptional()
  @Min(0, { message: 'El IVA no puede ser negativo' })
  @Max(100, { message: 'El IVA no puede ser mayor al 100%' })
  iva?: number = 0;

  @ApiPropertyOptional({ 
    description: 'Porcentaje de descuento aplicable', 
    example: 10,
    default: 0 
  })
  @IsOptional()
  @Min(0, { message: 'El descuento no puede ser negativo' })
  @Max(100, { message: 'El descuento no puede ser mayor al 100%' })
  descuento?: number = 0;

  @ApiProperty({ 
    description: 'ID de la factura a la que pertenece la línea', 
    example: '123e4567-e89b-12d3-a456-426614174000' 
  })
  @IsUUID('4', { message: 'El ID de la factura debe ser un UUID válido' })
  facturaId!: string;

  constructor(partial?: Partial<CreateLineaFacturaDto>) {
    if (partial) {
      Object.assign(this, {
        descripcion: partial.descripcion || '',
        cantidad: partial.cantidad || 0,
        precioUnitario: partial.precioUnitario || 0,
        iva: partial.iva || 0,
        descuento: partial.descuento || 0,
        facturaId: partial.facturaId || ''
      });
    }
  }
}
