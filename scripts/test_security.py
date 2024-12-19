import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.security.mfa import mfa_handler
from app.security.audit_log import audit_logger
from app.security.backup_manager import backup_manager
from app.database import SessionLocal
from app import models

def test_mfa():
    print("\n=== Probando MFA ===")
    # Simular un usuario de prueba
    test_email = "test@example.com"
    secret, qr_code = mfa_handler.generate_totp_secret(), "test_qr"
    print(f"✓ Secreto MFA generado: {secret[:10]}...")
    
    # Generar y verificar un token
    import pyotp
    totp = pyotp.TOTP(secret)
    token = totp.now()
    is_valid = mfa_handler.verify_totp(secret, token)
    print(f"✓ Verificación de token: {'Exitosa' if is_valid else 'Fallida'}")

def test_audit_logging():
    print("\n=== Probando Sistema de Logging ===")
    # Probar diferentes tipos de logs
    audit_logger.log_security_event(
        "test_event",
        "high",
        {"test": "data"},
        None
    )
    print("✓ Log de seguridad creado")
    
    # Verificar archivo de log
    log_file = Path('logs/audit.log')
    if log_file.exists():
        print(f"✓ Archivo de log creado en: {log_file}")
        print(f"✓ Tamaño del log: {log_file.stat().st_size} bytes")

def test_backup():
    print("\n=== Probando Sistema de Backup ===")
    # Realizar backup de prueba
    if backup_manager.backup_files():
        print("✓ Backup de archivos completado")
    
    # Verificar directorio de backups
    backup_dir = Path('backups')
    if backup_dir.exists():
        backups = list(backup_dir.glob('*'))
        print(f"✓ Número de backups: {len(backups)}")
        if backups:
            print(f"✓ Último backup: {backups[-1].name}")

def main():
    print("Iniciando pruebas de seguridad...")
    
    try:
        test_mfa()
    except Exception as e:
        print(f"✗ Error en prueba MFA: {str(e)}")
    
    try:
        test_audit_logging()
    except Exception as e:
        print(f"✗ Error en prueba de logging: {str(e)}")
    
    try:
        test_backup()
    except Exception as e:
        print(f"✗ Error en prueba de backup: {str(e)}")
    
    print("\nPruebas completadas.")

if __name__ == "__main__":
    main()
