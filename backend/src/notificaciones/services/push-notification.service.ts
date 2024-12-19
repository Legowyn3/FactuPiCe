import { Injectable, Logger } from '@nestjs/common';
import * as admin from 'firebase-admin';
import { ConfigService } from '@nestjs/config';
import { UserService } from '../../user/user.service';

interface NotificacionPushDatos {
  usuarioId: string;
  titulo: string;
  contenido: string;
  datos?: Record<string, any>;
}

@Injectable()
export class PushNotificationService {
  private readonly logger = new Logger(PushNotificationService.name);

  constructor(
    private configService: ConfigService,
    private userService: UserService
  ) {}

  private async inicializarFirebase() {
    if (!admin.apps.length) {
      try {
        admin.initializeApp({
          credential: admin.credential.cert({
            projectId: this.configService.get('FIREBASE_PROJECT_ID'),
            clientEmail: this.configService.get('FIREBASE_CLIENT_EMAIL'),
            privateKey: this.configService.get('FIREBASE_PRIVATE_KEY')?.replace(/\\n/g, '\n')
          })
        });
        this.logger.log('Firebase inicializado correctamente');
      } catch (error) {
        this.logger.error('Error inicializando Firebase', error);
        throw error;
      }
    }
  }

  async sendPushNotification(tokens: string[], title: string, body: string) {
    await this.inicializarFirebase();

    try {
      const messaging = admin.messaging();

      const messages = tokens.map(token => ({
        token,
        notification: {
          title,
          body
        }
      }));

      const response = await messaging.sendEach(messages);

      this.logger.log(`Successfully sent push notification: ${response.successCount} successful, ${response.failureCount} failed`);
      return response;
    } catch (error) {
      this.logger.error('Error sending push notification', error);
      throw error;
    }
  }

  async enviarNotificacionPush(datos: NotificacionPushDatos): Promise<void> {
    try {
      const tokenDispositivos = await this.userService.obtenerTokensPush(datos.usuarioId);

      if (tokenDispositivos.length === 0) {
        this.logger.warn(`No hay tokens de dispositivo para el usuario ${datos.usuarioId}`);
        return;
      }

      const respuesta = await this.sendPushNotification(
        tokenDispositivos, 
        datos.titulo, 
        datos.contenido
      );

      this.logger.log(`Notificaciones enviadas: ${respuesta.successCount}`);
      
      if (respuesta.failureCount > 0) {
        const tokensInvalidos = respuesta.responses
          .filter(resp => !resp.success)
          .map((resp, index) => ({ 
            token: tokenDispositivos[index], 
            error: resp.error 
          }));
        
        await this.userService.eliminarTokensPush(tokensInvalidos);
      }
    } catch (error) {
      this.logger.error('Error enviando notificación push', error);
      throw error;
    }
  }

  async suscribirDispositivo(usuarioId: string, token: string): Promise<void> {
    await this.userService.agregarTokenPush(usuarioId, token);
  }

  async desuscribirDispositivo(usuarioId: string, token: string): Promise<void> {
    await this.userService.eliminarTokenPush(usuarioId, token);
  }
}
