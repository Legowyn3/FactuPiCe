import { 
  Controller, 
  Get, 
  Post, 
  Body, 
  Patch, 
  Param, 
  Delete, 
  Query,
  UseGuards
} from '@nestjs/common';
import { 
  ApiTags, 
  ApiOperation, 
  ApiResponse, 
  ApiBearerAuth 
} from '@nestjs/swagger';
import { LineaFacturaService } from '../services/linea-factura.service';
import { CreateLineaFacturaDto } from '../dto/create-linea-factura.dto';
import { UpdateLineaFacturaDto } from '../dto/update-linea-factura.dto';
import { LineaFactura } from '../entities/linea-factura.entity';
import { JwtAuthGuard } from '../../auth/guards/jwt-auth.guard';

@ApiTags('Líneas de Factura')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('lineas-factura')
export class LineaFacturaController {
  constructor(private readonly lineaFacturaService: LineaFacturaService) {}

  @Post()
  @ApiOperation({ summary: 'Crear una nueva línea de factura' })
  @ApiResponse({ 
    status: 201, 
    description: 'Línea de factura creada exitosamente',
    type: LineaFactura 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Error al crear la línea de factura' 
  })
  async create(@Body() createLineaFacturaDto: CreateLineaFacturaDto): Promise<LineaFactura> {
    return this.lineaFacturaService.create(createLineaFacturaDto);
  }

  @Get()
  @ApiOperation({ summary: 'Obtener todas las líneas de factura' })
  @ApiResponse({ 
    status: 200, 
    description: 'Lista de líneas de factura',
    type: [LineaFactura] 
  })
  async findAll(@Query('facturaId') facturaId?: string): Promise<LineaFactura[]> {
    return this.lineaFacturaService.findAll(facturaId);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obtener una línea de factura por ID' })
  @ApiResponse({ 
    status: 200, 
    description: 'Detalles de la línea de factura',
    type: LineaFactura 
  })
  @ApiResponse({ 
    status: 404, 
    description: 'Línea de factura no encontrada' 
  })
  async findOne(@Param('id') id: string): Promise<LineaFactura> {
    return this.lineaFacturaService.findOne(id);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Actualizar una línea de factura' })
  @ApiResponse({ 
    status: 200, 
    description: 'Línea de factura actualizada exitosamente',
    type: LineaFactura 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Error al actualizar la línea de factura' 
  })
  async update(
    @Param('id') id: string, 
    @Body() updateLineaFacturaDto: UpdateLineaFacturaDto
  ): Promise<LineaFactura> {
    return this.lineaFacturaService.update(id, updateLineaFacturaDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Eliminar una línea de factura' })
  @ApiResponse({ 
    status: 200, 
    description: 'Línea de factura eliminada exitosamente' 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Error al eliminar la línea de factura' 
  })
  async remove(@Param('id') id: string): Promise<void> {
    return this.lineaFacturaService.remove(id);
  }

  @Patch(':id/descuento')
  @ApiOperation({ summary: 'Aplicar descuento a una línea de factura' })
  @ApiResponse({ 
    status: 200, 
    description: 'Descuento aplicado exitosamente',
    type: LineaFactura 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Error al aplicar descuento' 
  })
  async aplicarDescuento(
    @Param('id') id: string, 
    @Body('descuento') descuento: number
  ): Promise<LineaFactura> {
    return this.lineaFacturaService.aplicarDescuento(id, descuento);
  }
}
