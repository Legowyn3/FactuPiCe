import { IsString, IsDate, IsNumber, IsArray, IsOptional, ValidateNested, Min, Max } from 'class-validator';
import { Type } from 'class-transformer';
import { CreateConceptoFacturaDto } from './create-concepto-factura.dto';

export class CreateFacturaDto {
  @IsString()
  numero: string = '';

  @IsDate()
  @Type(() => Date)
  fecha: Date = new Date();

  @IsString()
  clienteId: string = '';

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => CreateConceptoFacturaDto)
  conceptos: CreateConceptoFacturaDto[] = [];

  @IsNumber()
  @Min(0)
  @Max(100)
  iva: number = 21;

  @IsNumber()
  @Min(0)
  @Max(100)
  retencion: number = 15;

  @IsString()
  @IsOptional()
  observaciones?: string = '';

  @IsOptional()
  sendEmail: boolean = false;

  constructor(partial: Partial<CreateFacturaDto> = {}) {
    const {
      numero = '',
      fecha = new Date(),
      clienteId = '',
      conceptos = [],
      iva = 21,
      retencion = 15,
      observaciones = '',
      sendEmail = false
    } = partial;

    this.numero = numero;
    this.fecha = fecha;
    this.clienteId = clienteId;
    this.conceptos = conceptos.map(c => new CreateConceptoFacturaDto(c));
    this.iva = iva;
    this.retencion = retencion;
    this.observaciones = observaciones;
    this.sendEmail = sendEmail;
  }

  get subtotal(): number {
    return this.conceptos.reduce((sum, concepto) => sum + concepto.subtotal, 0);
  }

  get totalIva(): number {
    return this.subtotal * (this.iva / 100);
  }

  get totalRetencion(): number {
    return this.subtotal * (this.retencion / 100);
  }

  get total(): number {
    return this.subtotal + this.totalIva - this.totalRetencion;
  }
}