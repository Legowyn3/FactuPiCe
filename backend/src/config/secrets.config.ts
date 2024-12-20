import * as dotenv from 'dotenv';
import * as crypto from 'crypto';

dotenv.config();

export class SecretsManager {
  private static instance: SecretsManager;
  private secretKey: string;

  private constructor() {
    // Generar clave de encriptación segura
    this.secretKey = this.generateSecureKey();
  }

  public static getInstance(): SecretsManager {
    if (!SecretsManager.instance) {
      SecretsManager.instance = new SecretsManager();
    }
    return SecretsManager.instance;
  }

  private generateSecureKey(): string {
    // Generar una clave segura usando variables de entorno
    const baseKey = process.env.SECRET_ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex');
    return crypto.createHash('sha256').update(baseKey).digest('hex');
  }

  // Método para encriptar secretos
  public encrypt(text: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-cbc', 
      Buffer.from(this.secretKey, 'hex'), 
      iv
    );
    
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    
    return iv.toString('hex') + ':' + encrypted.toString('hex');
  }

  // Método para desencriptar secretos
  public decrypt(text: string): string {
    const textParts = text.split(':');
    const iv = Buffer.from(textParts.shift(), 'hex');
    const encryptedText = Buffer.from(textParts.join(':'), 'hex');
    
    const decipher = crypto.createDecipheriv('aes-256-cbc', 
      Buffer.from(this.secretKey, 'hex'), 
      iv
    );
    
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    
    return decrypted.toString();
  }

  // Método para obtener secretos de forma segura
  public getSecret(key: string): string {
    const encryptedSecret = process.env[key];
    
    if (!encryptedSecret) {
      throw new Error(`Secret ${key} not found`);
    }

    try {
      return this.decrypt(encryptedSecret);
    } catch (error) {
      console.error(`Error decrypting secret ${key}:`, error);
      throw new Error(`Failed to decrypt secret ${key}`);
    }
  }

  // Método para establecer secretos de forma segura
  public setSecret(key: string, value: string): void {
    const encryptedValue = this.encrypt(value);
    process.env[key] = encryptedValue;
  }
}

// Ejemplo de uso
export const secretsManager = SecretsManager.getInstance();
