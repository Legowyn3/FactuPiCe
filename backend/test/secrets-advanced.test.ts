import { SecretsManager } from '../src/config/secrets.config';
import * as crypto from 'crypto';

describe('SecretsManager Avanzado', () => {
  let secretsManager: SecretsManager;

  beforeEach(() => {
    secretsManager = SecretsManager.getInstance();
  });

  // Pruebas de rendimiento
  describe('Rendimiento de Encriptación', () => {
    const testCases = [
      { name: 'Secreto Corto', secret: 'password123' },
      { name: 'Secreto Medio', secret: 'un_secreto_muy_largo_para_pruebas_de_rendimiento' },
      { name: 'Secreto Largo', secret: crypto.randomBytes(1024).toString('hex') }
    ];

    testCases.forEach(({ name, secret }) => {
      it(`Debe encriptar y desencriptar rápidamente: ${name}`, () => {
        const startTime = performance.now();
        
        const encryptedSecret = secretsManager.encrypt(secret);
        const decryptedSecret = secretsManager.decrypt(encryptedSecret);

        const endTime = performance.now();
        const duration = endTime - startTime;

        expect(decryptedSecret).toBe(secret);
        expect(duration).toBeLessThan(50); // Menos de 50ms
      });
    });
  });

  // Pruebas de seguridad
  describe('Seguridad de Secretos', () => {
    it('Debe generar encriptaciones diferentes para el mismo secreto', () => {
      const secret = 'secreto_repetido';
      
      const encrypted1 = secretsManager.encrypt(secret);
      const encrypted2 = secretsManager.encrypt(secret);

      expect(encrypted1).not.toBe(encrypted2);
      expect(secretsManager.decrypt(encrypted1)).toBe(secret);
      expect(secretsManager.decrypt(encrypted2)).toBe(secret);
    });

    it('Debe manejar caracteres especiales y Unicode', () => {
      const secretsToTest = [
        '¡Contraseña con caracteres especiales!',
        'パスワード123',
        'Emoji 🔐🚀',
        'SQL Injection Test\'; DROP TABLE users; --'
      ];

      secretsToTest.forEach(secret => {
        const encryptedSecret = secretsManager.encrypt(secret);
        const decryptedSecret = secretsManager.decrypt(encryptedSecret);

        expect(decryptedSecret).toBe(secret);
      });
    });

    it('Debe resistir intentos de manipulación', () => {
      const originalSecret = 'secreto_original';
      const encryptedSecret = secretsManager.encrypt(originalSecret);

      // Intentos de manipulación
      const tamperedSecrets = [
        encryptedSecret.slice(0, -5) + 'XXXX', // Modificar final
        'INVALID:' + encryptedSecret,          // Prefijo inválido
        encryptedSecret.replace(':', 'X')      // Cambiar separador
      ];

      tamperedSecrets.forEach(tamperedSecret => {
        expect(() => {
          secretsManager.decrypt(tamperedSecret);
        }).toThrow();
      });
    });
  });

  // Pruebas de gestión de secretos
  describe('Gestión de Secretos', () => {
    beforeEach(() => {
      // Limpiar variables de entorno antes de cada prueba
      delete process.env.TEST_MANAGEMENT_SECRET;
    });

    it('Debe establecer y recuperar secretos de forma segura', () => {
      const secretKey = 'TEST_MANAGEMENT_SECRET';
      const secretValue = 'valor_secreto_de_prueba';

      secretsManager.setSecret(secretKey, secretValue);

      // Verificar que el valor almacenado esté encriptado
      const storedSecret = process.env[secretKey];
      expect(storedSecret).not.toBe(secretValue);

      // Recuperar y desencriptar
      const retrievedSecret = secretsManager.getSecret(secretKey);
      expect(retrievedSecret).toBe(secretValue);
    });

    it('Debe manejar errores al recuperar secretos inexistentes', () => {
      expect(() => {
        secretsManager.getSecret('SECRETO_NO_EXISTENTE');
      }).toThrow('Secret SECRETO_NO_EXISTENTE not found');
    });
  });

  // Pruebas de rotación de claves
  describe('Rotación de Claves', () => {
    it('Debe mantener la capacidad de desencriptar secretos antiguos', () => {
      // Simular rotación de clave
      const originalKey = (secretsManager as any).secretKey;
      const secret = 'secreto_para_rotacion';

      // Encriptar con clave original
      const encryptedSecret = secretsManager.encrypt(secret);

      // Simular cambio de clave
      (secretsManager as any).secretKey = crypto.randomBytes(32).toString('hex');

      // Aún debe poder desencriptar
      const decryptedSecret = secretsManager.decrypt(encryptedSecret);
      expect(decryptedSecret).toBe(secret);
    });
  });
});
