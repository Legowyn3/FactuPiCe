import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn, CreateDateColumn } from 'typeorm';
import { User } from '../../user/entities/user.entity';

@Entity()
export class Notificacion {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  titulo: string;

  @Column('text')
  contenido: string;

  @Column({
    type: 'enum',
    enum: ['info', 'alerta', 'error', 'success'],
    default: 'info'
  })
  tipo: string;

  @Column({
    type: 'enum',
    enum: ['email', 'sms', 'push', 'in-app'],
    default: 'in-app'
  })
  canal: string;

  @Column()
  usuarioId: string;

  @ManyToOne(() => User)
  @JoinColumn({ name: 'usuarioId' })
  usuario: User;

  @Column({ default: false })
  leida: boolean;

  @CreateDateColumn()
  fechaCreacion: Date;
}
