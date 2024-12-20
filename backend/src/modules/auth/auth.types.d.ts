declare module 'auth' {
  import { Request } from '@nestjs/common';
  import { Usuario } from '../usuarios/entities/usuario.entity';

  export interface RequestWithUser extends Request {
    user: Omit<Usuario, 'password'>;
  }

  export interface JwtPayload {
    sub: string;
    email: string;
  }

  export interface AuthResponse {
    access_token: string;
    user: Omit<Usuario, 'password'>;
  }
} 