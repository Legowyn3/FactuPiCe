import { Controller, Get, Patch, Param, Query, Request, UseGuards } from '@nestjs/common';
import { NotificacionesService } from '../services/notificaciones.service';
import { JwtGuard } from '../../auth/guards/jwt.guard';

@Controller('notificaciones')
@UseGuards(JwtGuard)
export class NotificacionesController {
  constructor(
    private notificacionesService: NotificacionesService
  ) {}

  @Get()
  async obtenerNotificaciones(
    @Request() req,
    @Query('leidas') leidas?: boolean,
    @Query('tipo') tipo?: string
  ) {
    return this.notificacionesService.obtenerNotificacionesUsuario(
      req.user.id, 
      { leidas, tipo }
    );
  }

  @Patch(':id/marcar-leida')
  async marcarNotificacionComoLeida(
    @Param('id') notificacionId: string
  ) {
    return this.notificacionesService.marcarComoLeida(notificacionId);
  }
}
