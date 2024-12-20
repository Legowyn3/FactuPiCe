import { IsString, IsDate, IsNumber, IsArray, IsOptional, ValidateNested, Min, Max } from 'class-validator';
import { Type } from 'class-transformer';
import { CreateConceptoFacturaDto } from './create-concepto-factura.dto';
import { EstadoFactura } from '../entities/factura.entity';

export class UpdateFacturaDto {
  @IsOptional()
  @IsString()
  numero?: string;

  @IsOptional()
  @IsDate()
  @Type(() => Date)
  fecha?: Date;

  @IsOptional()
  @IsString()
  clienteId?: string;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => CreateConceptoFacturaDto)
  conceptos?: CreateConceptoFacturaDto[];

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  iva?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  retencion?: number;

  @IsOptional()
  @IsString()
  observaciones?: string;

  @IsOptional()
  estado?: EstadoFactura;

  constructor(partial: Partial<UpdateFacturaDto> = {}) {
    Object.assign(this, partial);
    
    if (partial.conceptos) {
      this.conceptos = partial.conceptos.map(c => new CreateConceptoFacturaDto(c));
    }
  }

  get subtotal(): number | undefined {
    return this.conceptos?.reduce((sum, concepto) => sum + concepto.subtotal, 0);
  }

  get totalIva(): number | undefined {
    return this.subtotal && this.iva ? this.subtotal * (this.iva / 100) : undefined;
  }

  get totalRetencion(): number | undefined {
    return this.subtotal && this.retencion ? this.subtotal * (this.retencion / 100) : undefined;
  }

  get total(): number | undefined {
    if (!this.subtotal) return undefined;
    return this.subtotal + (this.totalIva || 0) - (this.totalRetencion || 0);
  }
} 