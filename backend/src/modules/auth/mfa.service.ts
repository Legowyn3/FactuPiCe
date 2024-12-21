import { Injectable } from '@nestjs/common';
import * as speakeasy from 'speakeasy';
import * as QRCode from 'qrcode';

@Injectable()
export class MfaService {
  generateSecret(username: string) {
    const secret = speakeasy.generateSecret({ 
      name: `FactuPiCe: ${username}` 
    });

    return {
      secret: secret.base32,
      otpAuthUrl: secret.otpauth_url
    };
  }

  async generateQRCode(otpAuthUrl: string): Promise<string> {
    return QRCode.toDataURL(otpAuthUrl);
  }

  verifyToken(secret: string, token: string): boolean {
    return speakeasy.totp.verify({
      secret,
      encoding: 'base32',
      token
    });
  }
}
