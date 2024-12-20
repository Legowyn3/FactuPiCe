import { Usuario } from '../../usuarios/entities/usuario.entity';

export interface JwtPayload {
  sub: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  user: Omit<Usuario, 'password'>;
}

export interface LoginRequest {
  email: string;
  password: string;
} 