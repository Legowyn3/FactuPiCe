import { Injectable, Logger } from '@nestjs/common';
import { NotificacionesService } from '../../notificaciones/services/notificaciones.service';
import { EmailService } from '../../notificaciones/services/email.service';
import { PushNotificationService } from '../../notificaciones/services/push-notification.service';
import { ModelosFiscalesService } from '../../modelos-fiscales/services/modelos-fiscales.service';

@Injectable()
export class EventosFiscalesService {
  private readonly logger = new Logger(EventosFiscalesService.name);

  constructor(
    private notificacionesService: NotificacionesService,
    private emailService: EmailService,
    private pushService: PushNotificationService,
    private modelosFiscalesService: ModelosFiscalesService
  ) {}

  async manejarEventoFiscal(
    usuarioId: string, 
    tipoEvento: string, 
    datosEvento: any
  ) {
    let titulo = '';
    let contenido = '';
    let tipo: 'info' | 'alerta' | 'error' | 'success' = 'info';
    let canales: ('in-app' | 'email' | 'push')[] = ['in-app', 'email'];

    switch (tipoEvento) {
      case 'modelo_proximo_vencimiento':
        titulo = 'Modelo fiscal próximo a vencer';
        contenido = `El modelo ${datosEvento.modelo} vence el ${datosEvento.fechaVencimiento}`;
        tipo = 'alerta';
        break;
      
      case 'modelo_generado':
        titulo = 'Modelo fiscal generado';
        contenido = `Se ha generado el modelo ${datosEvento.modelo} para el ejercicio ${datosEvento.ejercicio}`;
        tipo = 'success';
        break;
      
      case 'error_generacion_modelo':
        titulo = 'Error en generación de modelo';
        contenido = `Hubo un problema al generar el modelo ${datosEvento.modelo}`;
        tipo = 'error';
        canales = ['in-app', 'email', 'push'];
        break;

      default:
        this.logger.warn(`Evento fiscal no reconocido: ${tipoEvento}`);
        return;
    }

    // Crear notificación en base de datos
    const notificacion = await this.notificacionesService.crearNotificacion({
      usuarioId,
      titulo,
      contenido,
      tipo
    });

    // Enviar notificaciones por diferentes canales
    for (const canal of canales) {
      try {
        switch (canal) {
          case 'email':
            await this.emailService.enviar({
              to: datosEvento.email,
              subject: titulo,
              template: 'evento-fiscal',
              context: {
                titulo,
                contenido,
                modelo: datosEvento.modelo,
                ejercicio: datosEvento.ejercicio
              }
            });
            break;

          case 'push':
            await this.pushService.enviar({
              usuarioId,
              titulo,
              contenido,
              datos: {
                tipoEvento,
                modeloId: datosEvento.modeloId
              }
            });
            break;
        }
      } catch (error) {
        this.logger.error(`Error enviando notificación por ${canal}`, error);
      }
    }

    return notificacion;
  }

  // Método para verificar vencimientos de modelos fiscales
  async verificarVencimientosModelos() {
    try {
      const modelosProximosAVencer = await this.modelosFiscalesService.obtenerModelosProximosAVencer();

      for (const modelo of modelosProximosAVencer) {
        await this.manejarEventoFiscal(
          modelo.usuarioId, 
          'modelo_proximo_vencimiento', 
          {
            modelo: modelo.tipo,
            fechaVencimiento: modelo.fechaVencimiento,
            email: modelo.usuario.email
          }
        );
      }
    } catch (error) {
      this.logger.error('Error verificando vencimientos de modelos', error);
    }
  }
}
