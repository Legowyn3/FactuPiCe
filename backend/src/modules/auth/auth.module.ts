import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';

import { AuthService } from './auth.service';
import { MfaService } from './mfa.service';
import { SecurityService } from './security.service';
import { AuthController } from './auth.controller';

import { Usuario } from '../usuarios/entities/usuario.entity';

import { LocalStrategy } from './strategies/local.strategy';
import { JwtStrategy } from './strategies/jwt.strategy';

@Module({
  imports: [
    TypeOrmModule.forFeature([Usuario]),
    PassportModule.register({ defaultStrategy: 'jwt' }),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        secret: configService.get<string>('JWT_SECRET'),
        signOptions: { 
          expiresIn: '1h',
          algorithm: 'HS256'
        },
      }),
      inject: [ConfigService],
    }),
    ConfigModule
  ],
  controllers: [AuthController],
  providers: [
    AuthService, 
    MfaService, 
    SecurityService,
    LocalStrategy,
    JwtStrategy
  ],
  exports: [AuthService, MfaService, SecurityService]
})
export class AuthModule {}