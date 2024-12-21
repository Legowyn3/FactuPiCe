import { 
  Controller, 
  Post, 
  Body, 
  UseGuards, 
  Request, 
  Get, 
  HttpCode, 
  HttpStatus,
  Param
} from '@nestjs/common';
import { AuthService } from './auth.service';
import { MfaService } from './mfa.service';
import { SecurityService } from './security.service';
import { LocalAuthGuard } from './guards/local-auth.guard';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('Autenticación')
@Controller('auth')
export class AuthController {
  constructor(
    private authService: AuthService,
    private mfaService: MfaService,
    private securityService: SecurityService
  ) {}

  @UseGuards(LocalAuthGuard)
  @Post('login')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Iniciar sesión' })
  @ApiResponse({ status: 200, description: 'Inicio de sesión exitoso' })
  @ApiResponse({ status: 401, description: 'Credenciales inválidas' })
  async login(@Request() req) {
    return this.authService.login(req.user);
  }

  @Post('refresh')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Refrescar token de acceso' })
  @ApiResponse({ status: 200, description: 'Token refrescado exitosamente' })
  @ApiResponse({ status: 401, description: 'Token inválido' })
  async refreshTokens(@Body() refreshTokenDto: RefreshTokenDto) {
    return this.authService.refreshTokens(
      refreshTokenDto.userId, 
      refreshTokenDto.refreshToken
    );
  }

  @UseGuards(JwtAuthGuard)
  @Post('mfa/setup')
  @ApiOperation({ summary: 'Configurar Multi-Factor Authentication' })
  async setupMfa(@Request() req) {
    const { secret, otpAuthUrl } = this.mfaService.generateSecret(req.user.username);
    const qrCode = await this.mfaService.generateQRCode(otpAuthUrl);

    return {
      secret,
      qrCode
    };
  }

  @Post('mfa/verify')
  @ApiOperation({ summary: 'Verificar token MFA' })
  async verifyMfaToken(
    @Body('secret') secret: string, 
    @Body('token') token: string
  ) {
    return this.mfaService.verifyToken(secret, token);
  }

  @UseGuards(JwtAuthGuard)
  @Post('logout')
  @ApiOperation({ summary: 'Cerrar sesión' })
  async logout(@Request() req) {
    await this.authService.revokeRefreshToken(req.user.id);
    return { message: 'Sesión cerrada exitosamente' };
  }

  @Get('security/status/:userId')
  @ApiOperation({ summary: 'Verificar estado de seguridad de cuenta' })
  async checkAccountStatus(@Param('userId') userId: number) {
    const isLocked = await this.securityService.checkAccountLock(userId);
    return { 
      userId, 
      isLocked 
    };
  }
}