import { 
  Controller, 
  Get, 
  Post, 
  Body, 
  Patch, 
  Param, 
  Delete, 
  UseGuards, 
  Query,
  UseInterceptors 
} from '@nestjs/common';
import { 
  ApiTags, 
  ApiOperation, 
  ApiResponse, 
  ApiQuery, 
  ApiBearerAuth 
} from '@nestjs/swagger';
import { ClientesService } from './clientes.service';
import { CreateClienteDto } from './dto/create-cliente.dto';
import { UpdateClienteDto } from './dto/update-cliente.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { Cliente } from './entities/cliente.entity';
import { ClienteFilterDto } from './specifications/cliente.specification';
import { LoggingInterceptor } from '../../common/interceptors/logging.interceptor';

@ApiTags('clientes')
@ApiBearerAuth()
@Controller('clientes')
@UseGuards(JwtAuthGuard)
@UseInterceptors(LoggingInterceptor)
export class ClientesController {
  constructor(private readonly clientesService: ClientesService) {}

  @Post()
  @ApiOperation({ summary: 'Crear un nuevo cliente' })
  @ApiResponse({ 
    status: 201, 
    description: 'Cliente creado exitosamente', 
    type: Cliente 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Datos de cliente inválidos' 
  })
  create(@Body() createClienteDto: CreateClienteDto) {
    return this.clientesService.create(createClienteDto);
  }

  @Get()
  @ApiOperation({ summary: 'Obtener lista de clientes con filtros avanzados' })
  @ApiQuery({ 
    name: 'nombre', 
    required: false, 
    type: String, 
    description: 'Filtrar por nombre' 
  })
  @ApiQuery({ 
    name: 'nif', 
    required: false, 
    type: String, 
    description: 'Filtrar por NIF/CIF/NIE' 
  })
  @ApiQuery({ 
    name: 'email', 
    required: false, 
    type: String, 
    description: 'Filtrar por email' 
  })
  @ApiQuery({ 
    name: 'telefono', 
    required: false, 
    type: String, 
    description: 'Filtrar por teléfono' 
  })
  @ApiQuery({ 
    name: 'minFacturas', 
    required: false, 
    type: Number, 
    description: 'Número mínimo de facturas' 
  })
  @ApiQuery({ 
    name: 'maxFacturas', 
    required: false, 
    type: Number, 
    description: 'Número máximo de facturas' 
  })
  @ApiQuery({ 
    name: 'createdAtFrom', 
    required: false, 
    type: Date, 
    description: 'Fecha de creación desde' 
  })
  @ApiQuery({ 
    name: 'createdAtTo', 
    required: false, 
    type: Date, 
    description: 'Fecha de creación hasta' 
  })
  @ApiQuery({ 
    name: 'page', 
    required: false, 
    type: Number, 
    description: 'Número de página' 
  })
  @ApiQuery({ 
    name: 'limit', 
    required: false, 
    type: Number, 
    description: 'Número de elementos por página' 
  })
  @ApiQuery({ 
    name: 'sortBy', 
    required: false, 
    type: String, 
    description: 'Campo para ordenar' 
  })
  @ApiQuery({ 
    name: 'sortOrder', 
    required: false, 
    enum: ['ASC', 'DESC'], 
    description: 'Orden de clasificación' 
  })
  @ApiResponse({ 
    status: 200, 
    description: 'Lista de clientes', 
    type: [Cliente] 
  })
  findAll(
    @Query('nombre') nombre?: string,
    @Query('nif') nif?: string,
    @Query('email') email?: string,
    @Query('telefono') telefono?: string,
    @Query('minFacturas') minFacturas?: number,
    @Query('maxFacturas') maxFacturas?: number,
    @Query('createdAtFrom') createdAtFrom?: Date,
    @Query('createdAtTo') createdAtTo?: Date,
    @Query('page') page?: number,
    @Query('limit') limit?: number,
    @Query('sortBy') sortBy?: keyof Cliente,
    @Query('sortOrder') sortOrder?: 'ASC' | 'DESC'
  ) {
    const filter: ClienteFilterDto = {
      nombre,
      nif,
      email,
      telefono,
      minFacturas,
      maxFacturas,
      createdAtFrom,
      createdAtTo
    };

    return this.clientesService.findAll(
      filter, 
      page, 
      limit, 
      sortBy, 
      sortOrder
    );
  }

  @Get(':id')
  @ApiOperation({ summary: 'Obtener un cliente por ID' })
  @ApiResponse({ 
    status: 200, 
    description: 'Cliente encontrado', 
    type: Cliente 
  })
  @ApiResponse({ 
    status: 404, 
    description: 'Cliente no encontrado' 
  })
  findOne(@Param('id') id: string) {
    return this.clientesService.findOne(id);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Actualizar un cliente' })
  @ApiResponse({ 
    status: 200, 
    description: 'Cliente actualizado', 
    type: Cliente 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'Datos de cliente inválidos' 
  })
  update(
    @Param('id') id: string, 
    @Body() updateClienteDto: UpdateClienteDto
  ) {
    return this.clientesService.update(id, updateClienteDto);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Eliminar un cliente' })
  @ApiResponse({ 
    status: 200, 
    description: 'Cliente eliminado' 
  })
  @ApiResponse({ 
    status: 400, 
    description: 'No se puede eliminar cliente con facturas asociadas' 
  })
  remove(@Param('id') id: string) {
    return this.clientesService.remove(id);
  }

  @Delete('soft/:id')
  @ApiOperation({ summary: 'Soft delete de un cliente' })
  @ApiResponse({ 
    status: 200, 
    description: 'Cliente marcado como eliminado' 
  })
  softDelete(@Param('id') id: string) {
    return this.clientesService.softDelete(id);
  }
}
