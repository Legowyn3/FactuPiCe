import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def setup_gpg():
    """Configurar GPG para cifrado de backups"""
    print("Configurando GPG para cifrado de backups...")
    
    # Obtener la clave de cifrado del archivo .env
    encryption_key = os.getenv('BACKUP_ENCRYPTION_KEY')
    if not encryption_key:
        print("Error: BACKUP_ENCRYPTION_KEY no encontrada en .env")
        return False
    
    try:
        # Verificar si gpg está instalado
        subprocess.run(['gpg', '--version'], check=True, capture_output=True)
        print("✓ GPG está instalado")
        
        # Generar archivo de configuración para gpg
        config = f"""Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: Backup System
Name-Email: backup@sistema-facturas.local
Expire-Date: 0
Passphrase: {encryption_key}
%commit
"""
        
        # Guardar configuración en archivo temporal
        config_path = 'gpg_config'
        with open(config_path, 'w') as f:
            f.write(config)
        
        # Generar par de claves
        subprocess.run(
            ['gpg', '--batch', '--gen-key', config_path],
            check=True,
            capture_output=True
        )
        print("✓ Par de claves GPG generado")
        
        # Limpiar archivo de configuración
        os.remove(config_path)
        print("✓ Archivo de configuración limpiado")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar gpg: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if setup_gpg():
        print("\n✓ Configuración de GPG completada exitosamente")
    else:
        print("\n✗ Error en la configuración de GPG")
