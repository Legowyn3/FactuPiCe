import { ExtractJwt, Strategy } from 'passport-jwt';
import { PassportStrategy } from '@nestjs/passport';
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Usuario } from '../../usuarios/entities/usuario.entity';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(
    private configService: ConfigService,
    @InjectRepository(Usuario)
    private usuarioRepository: Repository<Usuario>
  ) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: configService.get<string>('JWT_SECRET')
    });
  }

  async validate(payload: any) {
    // Buscar usuario en base de datos
    const usuario = await this.usuarioRepository.findOne({ 
      where: { 
        id: payload.sub,
        email: payload.email 
      },
      select: ['id', 'email', 'isActive', 'isLocked'] 
    });

    if (!usuario) {
      throw new UnauthorizedException('Usuario no encontrado');
    }

    // Verificar estado de la cuenta
    if (!usuario.isActive) {
      throw new UnauthorizedException('Cuenta desactivada');
    }

    if (usuario.isLocked) {
      throw new UnauthorizedException('Cuenta bloqueada');
    }

    return { 
      id: usuario.id, 
      email: usuario.email 
    };
  }
}