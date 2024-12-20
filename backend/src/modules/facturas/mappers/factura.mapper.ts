import { Injectable } from '@nestjs/common';
import { Factura } from '../entities/factura.entity';
import { CreateFacturaDto } from '../dto/create-factura.dto';
import { FacturaResponseDto } from '../dto/factura-response.dto';

@Injectable()
export class FacturaMapper {
  toEntity(dto: CreateFacturaDto): Partial<Factura> {
    const factura = new Factura();
    factura.numero = dto.numero;
    factura.fecha = dto.fecha;
    factura.clienteId = dto.clienteId;
    factura.iva = dto.iva;
    factura.retencion = dto.retencion;
    factura.observaciones = dto.observaciones;
    
    // Calcular totales
    const subtotal = dto.conceptos.reduce(
      (sum, concepto) => sum + (concepto.cantidad * concepto.precioUnitario),
      0
    );
    
    factura.subtotal = subtotal;
    factura.total = subtotal + (subtotal * dto.iva / 100) - (subtotal * dto.retencion / 100);
    
    return factura;
  }

  toDto(entity: Factura): FacturaResponseDto {
    return {
      id: entity.id,
      numero: entity.numero,
      fecha: entity.fecha,
      clienteId: entity.clienteId,
      cliente: entity.cliente,
      conceptos: entity.conceptos,
      subtotal: entity.subtotal,
      iva: entity.iva,
      retencion: entity.retencion,
      total: entity.total,
      estado: entity.estado,
      observaciones: entity.observaciones,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt
    };
  }
} 