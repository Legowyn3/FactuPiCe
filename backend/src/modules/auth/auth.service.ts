import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Usuario } from '../usuarios/entities/usuario.entity';
import { compare } from 'bcrypt';
import { JwtPayload, AuthResponse } from './types/auth.types';

@Injectable()
export class AuthService {
  constructor(
    @InjectRepository(Usuario)
    private usuarioRepository: Repository<Usuario>,
    private jwtService: JwtService
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
    const payload: JwtPayload = { email: user.email, sub: user.id };
    
    return {
      access_token: this.jwtService.sign(payload),
      user
    };
  }
} 