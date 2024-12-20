import { IsString, IsNumber, Min } from 'class-validator';

export class CreateConceptoFacturaDto {
  @IsString()
  descripcion: string = '';

  @IsNumber()
  @Min(1)
  cantidad: number = 1;

  @IsNumber()
  @Min(0)
  precioUnitario: number = 0;

  constructor(partial: Partial<CreateConceptoFacturaDto> = {}) {
    const { descripcion = '', cantidad = 1, precioUnitario = 0 } = partial;
    this.descripcion = descripcion;
    this.cantidad = cantidad;
    this.precioUnitario = precioUnitario;
  }

  get subtotal(): number {
    return this.cantidad * this.precioUnitario;
  }
} 