import { Injectable, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Usuario } from '../usuarios/entities/usuario.entity';

@Injectable()
export class SecurityService {
  private readonly logger = new Logger(SecurityService.name);

  constructor(
    @InjectRepository(Usuario)
    private usuarioRepository: Repository<Usuario>
  ) {}

  async logLoginAttempt(email: string, success: boolean): Promise<void> {
    const usuario = await this.usuarioRepository.findOne({ where: { email } });
    
    if (usuario) {
      usuario.lastLoginAttempt = new Date();
      usuario.failedLoginAttempts = success ? 0 : (usuario.failedLoginAttempts || 0) + 1;
      
      await this.usuarioRepository.save(usuario);

      if (usuario.failedLoginAttempts >= 5) {
        await this.lockAccount(usuario.id);
      }
    }
  }

  async lockAccount(userId: number): Promise<void> {
    await this.usuarioRepository.update(userId, {
      isLocked: true,
      lockedUntil: new Date(Date.now() + 30 * 60 * 1000) // 30 minutos
    });

    this.logger.warn(`Cuenta bloqueada: Usuario ID ${userId}`);
  }

  async unlockAccount(userId: number): Promise<void> {
    await this.usuarioRepository.update(userId, {
      isLocked: false,
      failedLoginAttempts: 0,
      lockedUntil: null
    });
  }

  async checkAccountLock(userId: number): Promise<boolean> {
    const usuario = await this.usuarioRepository.findOne({ 
      where: { id: userId },
      select: ['isLocked', 'lockedUntil'] 
    });

    if (!usuario || !usuario.isLocked) return false;

    if (usuario.lockedUntil && usuario.lockedUntil < new Date()) {
      await this.unlockAccount(userId);
      return false;
    }

    return true;
  }

  async rotateCredentials(userId: number, newPassword: string): Promise<void> {
    // Implementar lógica de rotación de credenciales
    // Incluye verificaciones de complejidad, historial de contraseñas, etc.
  }
}
