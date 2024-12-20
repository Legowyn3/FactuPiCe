import { SecretsManager } from '../src/config/secrets.config';

describe('SecretsManager', () => {
  let secretsManager: SecretsManager;

  beforeEach(() => {
    secretsManager = SecretsManager.getInstance();
  });

  it('debe encriptar y desencriptar un secreto correctamente', () => {
    const originalSecret = 'mi_secreto_super_seguro_2024';
    
    // Encriptar
    const encryptedSecret = secretsManager.encrypt(originalSecret);
    expect(encryptedSecret).toBeTruthy();
    expect(encryptedSecret).not.toBe(originalSecret);

    // Desencriptar
    const decryptedSecret = secretsManager.decrypt(encryptedSecret);
    expect(decryptedSecret).toBe(originalSecret);
  });

  it('debe manejar secretos desde variables de entorno', () => {
    // Configurar un secreto en las variables de entorno
    process.env.TEST_SECRET = secretsManager.encrypt('secreto_de_prueba');

    // Obtener y desencriptar
    const retrievedSecret = secretsManager.getSecret('TEST_SECRET');
    expect(retrievedSecret).toBe('secreto_de_prueba');
  });

  it('debe generar diferentes encriptaciones para el mismo texto', () => {
    const secret = 'texto_secreto';
    
    const encrypted1 = secretsManager.encrypt(secret);
    const encrypted2 = secretsManager.encrypt(secret);

    expect(encrypted1).not.toBe(encrypted2);
    expect(secretsManager.decrypt(encrypted1)).toBe(secret);
    expect(secretsManager.decrypt(encrypted2)).toBe(secret);
  });

  it('debe lanzar un error al intentar desencriptar un secreto inválido', () => {
    expect(() => {
      secretsManager.decrypt('secreto_invalido');
    }).toThrow();
  });
});
