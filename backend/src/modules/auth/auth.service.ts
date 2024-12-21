import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Usuario } from '../usuarios/entities/usuario.entity';
import { compare, hash } from 'bcrypt';
import { JwtPayload, AuthResponse } from './types/auth.types';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(Usuario)
    private usuarioRepository: Repository<Usuario>,
    private jwtService: JwtService,
    private configService: ConfigService
  ) {}

  async validateUser(email: string, password: string): Promise<Omit<Usuario, 'password'> | null> {
    const usuario = await this.usuarioRepository.findOne({ where: { email } });
    
    if (usuario && await compare(password, usuario.password)) {
      const { password: _, ...result } = usuario;
      return result;
    }
    
    return null;
  }

  async login(user: Omit<Usuario, 'password'>): Promise<AuthResponse> {
    const payload: JwtPayload = { 
      email: user.email, 
      sub: user.id 
    };
    
    const accessToken = this.generateAccessToken(payload);
    const refreshToken = this.generateRefreshToken(payload);

    // Guardar refresh token hasheado en la base de datos
    await this.storeRefreshToken(user.id, refreshToken);

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      user
    };
  }

  private generateAccessToken(payload: JwtPayload): string {
    return this.jwtService.sign(payload, {
      secret: this.configService.get<string>('JWT_ACCESS_SECRET'),
      expiresIn: '15m' // Token de acceso de corta duración
    });
  }

  private generateRefreshToken(payload: JwtPayload): string {
    return this.jwtService.sign(payload, {
      secret: this.configService.get<string>('JWT_REFRESH_SECRET'),
      expiresIn: '7d' // Token de refresco de larga duración
    });
  }

  async refreshTokens(userId: number, refreshToken: string): Promise<AuthResponse> {
    const user = await this.usuarioRepository.findOne({ 
      where: { id: userId },
      select: ['id', 'email'] 
    });

    if (!user) {
      throw new UnauthorizedException('Usuario no encontrado');
    }

    // Verificar si el refresh token es válido
    try {
      const isRefreshTokenValid = await this.verifyRefreshToken(userId, refreshToken);
      
      if (!isRefreshTokenValid) {
        throw new UnauthorizedException('Token de refresco inválido');
      }

      const payload: JwtPayload = { 
        email: user.email, 
        sub: user.id 
      };

      const newAccessToken = this.generateAccessToken(payload);
      const newRefreshToken = this.generateRefreshToken(payload);

      // Actualizar refresh token en base de datos
      await this.storeRefreshToken(user.id, newRefreshToken);

      return {
        access_token: newAccessToken,
        refresh_token: newRefreshToken,
        user
      };

    } catch (error) {
      throw new UnauthorizedException('No se pudo refrescar los tokens');
    }
  }

  private async storeRefreshToken(userId: number, refreshToken: string): Promise<void> {
    const hashedToken = await hash(refreshToken, 10);
    
    await this.usuarioRepository.update(userId, {
      refreshToken: hashedToken
    });
  }

  private async verifyRefreshToken(userId: number, refreshToken: string): Promise<boolean> {
    const user = await this.usuarioRepository.findOne({ 
      where: { id: userId },
      select: ['refreshToken'] 
    });

    if (!user || !user.refreshToken) {
      return false;
    }

    return compare(refreshToken, user.refreshToken);
  }

  async revokeRefreshToken(userId: number): Promise<void> {
    await this.usuarioRepository.update(userId, {
      refreshToken: null
    });
  }
}