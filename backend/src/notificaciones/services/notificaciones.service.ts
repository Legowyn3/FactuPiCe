import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Notificacion } from '../entities/notificacion.entity';
import { User } from '../../user/entities/user.entity';
import { UserService } from '../../user/user.service';
import { PushNotificationService } from './push-notification.service';

@Injectable()
export class NotificacionesService {
  constructor(
    @InjectRepository(Notificacion)
    private notificacionRepository: Repository<Notificacion>,
    private userService: UserService,
    private pushNotificationService: PushNotificationService
  ) {}

  async crearNotificacion(
    datos: {
      usuarioId: string;
      titulo: string;
      contenido: string;
      tipo?: string;
      canal?: string;
      enviarPush?: boolean;
    }
  ): Promise<Notificacion> {
    const { enviarPush, ...notificacionDatos } = datos;

    const notificacion = this.notificacionRepository.create({
      ...notificacionDatos,
      leida: false
    });

    const notificacionGuardada = await this.notificacionRepository.save(notificacion);

    // Enviar notificación push si está habilitado
    if (enviarPush) {
      await this.enviarNotificacionPush(notificacionGuardada);
    }

    return notificacionGuardada;
  }

  private async enviarNotificacionPush(notificacion: Notificacion) {
    await this.pushNotificationService.enviarNotificacionPush({
      usuarioId: notificacion.usuarioId,
      titulo: notificacion.titulo,
      contenido: notificacion.contenido,
      datos: {
        notificacionId: notificacion.id,
        tipo: notificacion.tipo
      }
    });
  }

  async marcarComoLeida(notificacionId: string) {
    await this.notificacionRepository.update(
      notificacionId, 
      { leida: true }
    );
  }

  async obtenerNotificacionesUsuario(
    usuarioId: string, 
    filtros?: {
      leidas?: boolean;
      tipo?: string;
    }
  ) {
    return this.notificacionRepository.find({
      where: {
        usuarioId,
        ...(filtros?.leidas !== undefined && { leida: filtros.leidas }),
        ...(filtros?.tipo && { tipo: filtros.tipo })
      },
      order: { fechaCreacion: 'DESC' }
    });
  }
}
