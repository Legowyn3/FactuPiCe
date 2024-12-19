import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Notificacion } from './entities/notificacion.entity';
import { NotificacionesService } from './services/notificaciones.service';
import { NotificacionesController } from './controllers/notificaciones.controller';
import { EmailService } from './services/email.service';
import { PushNotificationService } from './services/push-notification.service';
import { UsuariosModule } from '../usuarios/usuarios.module';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    TypeOrmModule.forFeature([Notificacion]),
    UsuariosModule,
    ConfigModule
  ],
  controllers: [NotificacionesController],
  providers: [
    NotificacionesService,
    EmailService,
    PushNotificationService
  ],
  exports: [
    NotificacionesService,
    EmailService,
    PushNotificationService
  ]
})
export class NotificacionesModule {}
