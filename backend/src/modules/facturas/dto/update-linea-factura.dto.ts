import { IsNotEmpty, IsPositive, Min, Max, IsOptional, IsUUID } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { PartialType } from '@nestjs/mapped-types';
import { CreateLineaFacturaDto } from './create-linea-factura.dto';

export class UpdateLineaFacturaDto extends PartialType(CreateLineaFacturaDto) {
  @ApiPropertyOptional({ 
    description: 'ID único de la línea de factura', 
    example: '123e4567-e89b-12d3-a456-426614174000' 
  })
  @IsOptional()
  @IsUUID('4', { message: 'El ID de la línea de factura debe ser un UUID válido' })
  id?: string;

  @ApiPropertyOptional({ 
    description: 'Subtotal de la línea de factura', 
    example: 200.75 
  })
  @IsOptional()
  @IsPositive({ message: 'El subtotal debe ser un número positivo' })
  subtotal?: number;

  constructor(partial?: Partial<UpdateLineaFacturaDto>) {
    super();
    if (partial) {
      Object.assign(this, {
        id: partial.id,
        subtotal: partial.subtotal,
        ...partial
      });
    }
  }
}
