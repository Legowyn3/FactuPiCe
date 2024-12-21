import { Strategy } from 'passport-local';
import { PassportStrategy } from '@nestjs/passport';
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { AuthService } from '../auth.service';
import { SecurityService } from '../security.service';

@Injectable()
export class LocalStrategy extends PassportStrategy(Strategy) {
  constructor(
    private authService: AuthService,
    private securityService: SecurityService
  ) {
    super({ 
      usernameField: 'email',
      passwordField: 'password'
    });
  }

  async validate(email: string, password: string): Promise<any> {
    const user = await this.authService.validateUser(email, password);
    
    if (!user) {
      // Registrar intento fallido de inicio de sesión
      await this.securityService.logLoginAttempt(email, false);
      throw new UnauthorizedException('Credenciales inválidas');
    }

    // Verificar si la cuenta está bloqueada
    const isLocked = await this.securityService.checkAccountLock(user.id);
    if (isLocked) {
      throw new UnauthorizedException('Cuenta bloqueada. Contacte al administrador.');
    }

    // Registrar inicio de sesión exitoso
    await this.securityService.logLoginAttempt(email, true);

    return user;
  }
}