import { CreateFacturaDto } from './create-factura.dto';
import { CreateConceptoFacturaDto } from './create-concepto-factura.dto';

// Tipos base
export type FacturaBase = {
  numero: string;
  fecha: Date;
  clienteId: string;
  conceptos: CreateConceptoFacturaDto[];
  iva: number;
  retencion: number;
  observaciones?: string;
};

// Tipo para actualización parcial
export type UpdateFacturaDto = Partial<FacturaBase>;

export {
  CreateFacturaDto,
  CreateConceptoFacturaDto
}; 