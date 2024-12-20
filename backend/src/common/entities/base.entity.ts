import { 
  PrimaryGeneratedColumn, 
  CreateDateColumn, 
  UpdateDateColumn, 
  BaseEntity as TypeOrmBaseEntity 
} from 'typeorm';
import { Exclude } from 'class-transformer';

export abstract class BaseEntity extends TypeOrmBaseEntity {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @CreateDateColumn({ 
    type: 'timestamp', 
    name: 'fecha_creacion',
    select: true 
  })
  fechaCreacion: Date;

  @UpdateDateColumn({ 
    type: 'timestamp', 
    name: 'fecha_actualizacion',
    select: true 
  })
  fechaActualizacion: Date;

  @Exclude()
  public softDelete(): void {
    // Método para soft delete, puede ser sobrescrito
    (this as any).activo = false;
  }

  // Método para serialización consistente
  toJSON() {
    const { ...entityWithoutBaseFields } = this;
    return entityWithoutBaseFields;
  }
}
