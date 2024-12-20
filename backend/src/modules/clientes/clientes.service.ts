import { 
  Injectable, 
  NotFoundException, 
  BadRequestException,
  Inject 
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { Cliente } from './entities/cliente.entity';
import { CreateClienteDto } from './dto/create-cliente.dto';
import { UpdateClienteDto } from './dto/update-cliente.dto';
import { 
  ClienteFilterDto, 
  ClienteSpecification 
} from './specifications/cliente.specification';
import { CacheKeys } from '../../config/cache.config';

@Injectable()
export class ClientesService {
  constructor(
    @InjectRepository(Cliente)
    private clientesRepository: Repository<Cliente>,
    @Inject(CACHE_MANAGER)
    private cacheManager: Cache
  ) {}

  async create(createClienteDto: CreateClienteDto): Promise<Cliente> {
    // Validar NIF único
    const existingCliente = await this.clientesRepository.findOne({ 
      where: { nif: createClienteDto.nif } 
    });
    
    if (existingCliente) {
      throw new BadRequestException(`Ya existe un cliente con NIF ${createClienteDto.nif}`);
    }

    const cliente = this.clientesRepository.create(createClienteDto);
    const savedCliente = await this.clientesRepository.save(cliente);

    // Invalidar caché de lista de clientes
    await this.cacheManager.del(CacheKeys.CLIENTE_LIST);

    return savedCliente;
  }

  async findAll(
    filter: ClienteFilterDto = {}, 
    page = 1, 
    limit = 10, 
    sortBy?: keyof Cliente, 
    sortOrder: 'ASC' | 'DESC' = 'ASC'
  ): Promise<{ 
    data: Cliente[], 
    total: number, 
    page: number, 
    totalPages: number 
  }> {
    // Generar clave de caché única basada en parámetros
    const cacheKey = `${CacheKeys.CLIENTE_LIST}_${JSON.stringify(filter)}_${page}_${limit}_${sortBy}_${sortOrder}`;

    // Intentar obtener de caché
    const cachedResult = await this.cacheManager.get(cacheKey);
    if (cachedResult) {
      return cachedResult as { 
        data: Cliente[], 
        total: number, 
        page: number, 
        totalPages: number 
      };
    }

    const specification = ClienteSpecification.createSpecification(
      filter, 
      page, 
      limit, 
      sortBy, 
      sortOrder
    );

    const [data, total] = await this.clientesRepository.findAndCount(specification);

    const result = {
      data,
      total,
      page,
      totalPages: Math.ceil(total / limit)
    };

    // Guardar en caché
    await this.cacheManager.set(cacheKey, result);

    return result;
  }

  async findOne(id: string): Promise<Cliente> {
    // Intentar obtener de caché
    const cachedCliente = await this.cacheManager.get(`${CacheKeys.CLIENTE_DETAIL}_${id}`);
    if (cachedCliente) {
      return cachedCliente as Cliente;
    }

    const cliente = await this.clientesRepository.findOne({ 
      where: { id },
      relations: ['facturas'] // Incluir facturas relacionadas
    });
    
    if (!cliente) {
      throw new NotFoundException(`Cliente con ID ${id} no encontrado`);
    }

    // Guardar en caché
    await this.cacheManager.set(`${CacheKeys.CLIENTE_DETAIL}_${id}`, cliente);

    return cliente;
  }

  async update(id: string, updateClienteDto: UpdateClienteDto): Promise<Cliente> {
    const cliente = await this.findOne(id);

    // Validar NIF único si se cambia
    if (updateClienteDto.nif && updateClienteDto.nif !== cliente.nif) {
      const existingCliente = await this.clientesRepository.findOne({ 
        where: { nif: updateClienteDto.nif } 
      });
      
      if (existingCliente) {
        throw new BadRequestException(`Ya existe un cliente con NIF ${updateClienteDto.nif}`);
      }
    }

    const updatedCliente = this.clientesRepository.merge(cliente, updateClienteDto);
    const savedCliente = await this.clientesRepository.save(updatedCliente);

    // Invalidar caché
    await Promise.all([
      this.cacheManager.del(`${CacheKeys.CLIENTE_DETAIL}_${id}`),
      this.cacheManager.del(CacheKeys.CLIENTE_LIST)
    ]);

    return savedCliente;
  }

  async remove(id: string): Promise<void> {
    const cliente = await this.findOne(id);
    
    // Verificar si el cliente tiene facturas antes de eliminar
    if (cliente.facturas && cliente.facturas.length > 0) {
      throw new BadRequestException(`No se puede eliminar el cliente con ID ${id} porque tiene facturas asociadas`);
    }

    await this.clientesRepository.remove(cliente);

    // Invalidar caché
    await Promise.all([
      this.cacheManager.del(`${CacheKeys.CLIENTE_DETAIL}_${id}`),
      this.cacheManager.del(CacheKeys.CLIENTE_LIST)
    ]);
  }

  // Método para soft delete (opcional)
  async softDelete(id: string): Promise<void> {
    const result = await this.clientesRepository.softDelete(id);
    
    if (result.affected === 0) {
      throw new NotFoundException(`Cliente con ID ${id} no encontrado`);
    }

    // Invalidar caché
    await Promise.all([
      this.cacheManager.del(`${CacheKeys.CLIENTE_DETAIL}_${id}`),
      this.cacheManager.del(CacheKeys.CLIENTE_LIST)
    ]);
  }
}
