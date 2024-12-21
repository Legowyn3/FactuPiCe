import { Test, TestingModule } from '@nestjs/testing';
import { AuthService } from '../../src/modules/auth/auth.service';
import { MfaService } from '../../src/modules/auth/mfa.service';
import { SecurityService } from '../../src/modules/auth/security.service';
import { JwtService } from '@nestjs/jwt';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Usuario } from '../../src/modules/usuarios/entities/usuario.entity';
import { ConfigService } from '@nestjs/config';

describe('AuthService', () => {
  let authService: AuthService;
  let mfaService: MfaService;
  let securityService: SecurityService;

  const mockUserRepository = {
    findOne: jest.fn(),
    update: jest.fn(),
  };

  const mockJwtService = {
    sign: jest.fn(),
  };

  const mockConfigService = {
    get: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        MfaService,
        SecurityService,
        {
          provide: getRepositoryToken(Usuario),
          useValue: mockUserRepository,
        },
        {
          provide: JwtService,
          useValue: mockJwtService,
        },
        {
          provide: ConfigService,
          useValue: mockConfigService,
        },
      ],
    }).compile();

    authService = module.get<AuthService>(AuthService);
    mfaService = module.get<MfaService>(MfaService);
    securityService = module.get<SecurityService>(SecurityService);
  });

  it('should generate access and refresh tokens', async () => {
    const mockUser = { 
      id: 1, 
      email: 'test@example.com',
      nombre: 'Test User',
      mfaEnabled: false,
      failedLoginAttempts: 0,
      isLocked: false,
      isActive: true
    } as Usuario;

    mockUserRepository.findOne.mockResolvedValue(mockUser);
    mockJwtService.sign.mockReturnValue('mock_token');
    mockConfigService.get.mockReturnValue('secret');

    const result = await authService.login(mockUser);

    expect(result.access_token).toBeDefined();
    expect(result.user).toEqual(mockUser);
  });

  it('should refresh tokens', async () => {
    const mockUser = { 
      id: 1, 
      email: 'test@example.com',
      nombre: 'Test User',
      mfaEnabled: false,
      failedLoginAttempts: 0,
      isLocked: false,
      isActive: true
    } as Usuario;

    mockUserRepository.findOne.mockResolvedValue(mockUser);
    mockJwtService.sign.mockReturnValue('new_mock_token');
    mockConfigService.get.mockReturnValue('secret');

    const result = await authService.refreshTokens(1, 'old_refresh_token');

    expect(result.access_token).toBeDefined();
  });

  it('should generate MFA secret', () => {
    const secret = mfaService.generateSecret('testuser');

    expect(secret.secret).toBeDefined();
    expect(secret.otpAuthUrl).toBeDefined();
  });

  it('should check account lock status', async () => {
    mockUserRepository.findOne.mockResolvedValue({ 
      isLocked: false 
    });

    const isLocked = await securityService.checkAccountLock(1);

    expect(isLocked).toBeFalsy();
  });
});
