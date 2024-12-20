import { 
  Injectable, 
  NotFoundException, 
  BadRequestException,
  InternalServerErrorException 
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { LineaFactura } from '../entities/linea-factura.entity';
import { Factura } from '../entities/factura.entity';
import { CreateLineaFacturaDto } from '../dto/create-linea-factura.dto';
import { UpdateLineaFacturaDto } from '../dto/update-linea-factura.dto';

@Injectable()
export class LineaFacturaService {
  constructor(
    @InjectRepository(LineaFactura)
    private lineaFacturaRepository: Repository<LineaFactura>,
    @InjectRepository(Factura)
    private facturaRepository: Repository<Factura>
  ) {}

  async create(createLineaFacturaDto: CreateLineaFacturaDto): Promise<LineaFactura> {
    // Verificar que la factura existe
    const factura = await this.facturaRepository.findOne({ 
      where: { id: createLineaFacturaDto.facturaId } 
    });

    if (!factura) {
      throw new NotFoundException(`Factura con ID ${createLineaFacturaDto.facturaId} no encontrada`);
    }

    // Crear la línea de factura
    const lineaFactura = this.lineaFacturaRepository.create({
      ...createLineaFacturaDto,
      factura,
      subtotal: createLineaFacturaDto.cantidad * createLineaFacturaDto.precioUnitario
    });

    try {
      const savedLineaFactura = await this.lineaFacturaRepository.save(lineaFactura);
      
      // Actualizar totales de la factura
      factura.lineas.push(savedLineaFactura);
      factura.calcularTotales();
      await this.facturaRepository.save(factura);

      return savedLineaFactura;
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new BadRequestException(`Error al crear la línea de factura: ${error.message}`);
      }
      throw new InternalServerErrorException('Error desconocido al crear la línea de factura');
    }
  }

  async findAll(facturaId?: string): Promise<LineaFactura[]> {
    if (facturaId) {
      return this.lineaFacturaRepository.find({ 
        where: { factura: { id: facturaId } },
        relations: ['factura']
      });
    }
    return this.lineaFacturaRepository.find({ relations: ['factura'] });
  }

  async findOne(id: string): Promise<LineaFactura> {
    const lineaFactura = await this.lineaFacturaRepository.findOne({ 
      where: { id },
      relations: ['factura']
    });

    if (!lineaFactura) {
      throw new NotFoundException(`Línea de factura con ID ${id} no encontrada`);
    }

    return lineaFactura;
  }

  async update(id: string, updateLineaFacturaDto: UpdateLineaFacturaDto): Promise<LineaFactura> {
    const lineaFactura = await this.findOne(id);

    // Actualizar campos
    Object.assign(lineaFactura, updateLineaFacturaDto);

    // Recalcular subtotal si es necesario
    if (updateLineaFacturaDto.cantidad || updateLineaFacturaDto.precioUnitario) {
      lineaFactura.calcularSubtotal();
    }

    try {
      const savedLineaFactura = await this.lineaFacturaRepository.save(lineaFactura);
      
      // Actualizar totales de la factura
      const factura = await this.facturaRepository.findOne({ 
        where: { id: lineaFactura.factura.id },
        relations: ['lineas']
      });

      if (factura) {
        factura.calcularTotales();
        await this.facturaRepository.save(factura);
      }

      return savedLineaFactura;
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new BadRequestException(`Error al actualizar la línea de factura: ${error.message}`);
      }
      throw new InternalServerErrorException('Error desconocido al actualizar la línea de factura');
    }
  }

  async remove(id: string): Promise<void> {
    const lineaFactura = await this.findOne(id);

    try {
      await this.lineaFacturaRepository.remove(lineaFactura);
      
      // Actualizar totales de la factura
      const factura = await this.facturaRepository.findOne({ 
        where: { id: lineaFactura.factura.id },
        relations: ['lineas']
      });

      if (factura) {
        factura.calcularTotales();
        await this.facturaRepository.save(factura);
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new BadRequestException(`Error al eliminar la línea de factura: ${error.message}`);
      }
      throw new InternalServerErrorException('Error desconocido al eliminar la línea de factura');
    }
  }

  async aplicarDescuento(id: string, descuento: number): Promise<LineaFactura> {
    const lineaFactura = await this.findOne(id);

    try {
      const subtotalConDescuento = lineaFactura.aplicarDescuento(descuento);
      const savedLineaFactura = await this.lineaFacturaRepository.save(lineaFactura);
      
      // Actualizar totales de la factura
      const factura = await this.facturaRepository.findOne({ 
        where: { id: lineaFactura.factura.id },
        relations: ['lineas']
      });

      if (factura) {
        factura.calcularTotales();
        await this.facturaRepository.save(factura);
      }

      return savedLineaFactura;
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new BadRequestException(error.message);
      }
      throw new InternalServerErrorException('Error desconocido al aplicar descuento');
    }
  }
}
