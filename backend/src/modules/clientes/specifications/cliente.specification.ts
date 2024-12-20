import { 
  FindManyOptions, 
  FindOptionsWhere, 
  Like, 
  MoreThanOrEqual, 
  LessThanOrEqual 
} from 'typeorm';
import { Cliente } from '../entities/cliente.entity';

export interface ClienteFilterDto {
  nombre?: string;
  nif?: string;
  email?: string;
  telefono?: string;
  minFacturas?: number;
  maxFacturas?: number;
  createdAtFrom?: Date;
  createdAtTo?: Date;
}

export class ClienteSpecification {
  static createSpecification(
    filter: ClienteFilterDto, 
    page = 1, 
    limit = 10, 
    sortBy: keyof Cliente = 'createdAt', 
    sortOrder: 'ASC' | 'DESC' = 'DESC'
  ): FindManyOptions<Cliente> {
    const skip = (page - 1) * limit;
    const where: FindOptionsWhere<Cliente>[] = [];

    // Filtros básicos
    if (filter.nombre) {
      where.push({ nombre: Like(`%${filter.nombre}%`) });
    }

    if (filter.nif) {
      where.push({ nif: Like(`%${filter.nif}%`) });
    }

    if (filter.email) {
      where.push({ email: Like(`%${filter.email}%`) });
    }

    if (filter.telefono) {
      where.push({ telefono: Like(`%${filter.telefono}%`) });
    }

    // Filtros de fechas
    const dateConditions: FindOptionsWhere<Cliente> = {};
    if (filter.createdAtFrom) {
      dateConditions.createdAt = MoreThanOrEqual(filter.createdAtFrom);
    }
    if (filter.createdAtTo) {
      dateConditions.createdAt = LessThanOrEqual(filter.createdAtTo);
    }

    if (Object.keys(dateConditions).length > 0) {
      where.push(dateConditions);
    }

    return {
      where,
      order: { [sortBy]: sortOrder },
      skip,
      take: limit,
      relations: ['facturas'],
      loadEagerRelations: false,
      select: {
        id: true,
        nombre: true,
        nif: true,
        email: true,
        telefono: true,
        direccion: true,
        createdAt: true,
        facturas: {
          id: true,
          total: true
        }
      },
      // Filtro adicional por número de facturas
      ...(filter.minFacturas !== undefined || filter.maxFacturas !== undefined 
        ? { 
            where: where.map(w => ({
              ...w,
              facturas: {
                ...(filter.minFacturas !== undefined 
                  ? { length: MoreThanOrEqual(filter.minFacturas) } 
                  : {}),
                ...(filter.maxFacturas !== undefined 
                  ? { length: LessThanOrEqual(filter.maxFacturas) } 
                  : {})
              }
            }))
          } 
        : {})
    };
  }
}
