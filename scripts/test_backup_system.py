import os
import sys
import pytest
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from app.backup.backup_manager import backup_manager
from app.logging.logger import security_logger

def test_backup_directories_exist():
    """Verificar que los directorios de backup existen"""
    base_dir = Path(__file__).parent.parent
    backup_dir = base_dir / 'app' / 'backups'
    temp_dir = backup_dir / 'temp'
    
    assert backup_dir.exists(), "El directorio de backups no existe"
    assert temp_dir.exists(), "El directorio temporal de backups no existe"

def test_backup_permissions():
    """Verificar que los permisos de los directorios son seguros"""
    base_dir = Path(__file__).parent.parent
    backup_dir = base_dir / 'app' / 'backups'
    
    mode = oct(backup_dir.stat().st_mode)[-3:]
    assert mode == '700', f"Los permisos del directorio de backups son {mode}, deberían ser 700"

def test_database_backup():
    """Probar el backup de la base de datos"""
    try:
        backup_info = backup_manager.backup_database()
        assert backup_info['success'], "El backup de la base de datos falló"
        assert Path(backup_info['file_path']).exists(), "El archivo de backup no existe"
    except Exception as e:
        pytest.fail(f"Error al realizar backup de la base de datos: {e}")

def test_logs_backup():
    """Probar el backup de los logs"""
    try:
        backup_info = backup_manager.backup_logs()
        assert backup_info['success'], "El backup de logs falló"
        assert Path(backup_info['file_path']).exists(), "El archivo de backup no existe"
    except Exception as e:
        pytest.fail(f"Error al realizar backup de logs: {e}")

def test_backup_encryption():
    """Verificar que los backups están encriptados"""
    try:
        backup_info = backup_manager.backup_database()
        backup_file = Path(backup_info['file_path'])
        
        # Verificar que el archivo tiene la extensión .gpg
        assert backup_file.suffix == '.gpg', "El backup no está encriptado con GPG"
        
        # Intentar leer el contenido del archivo (debería estar encriptado)
        with open(backup_file, 'rb') as f:
            content = f.read(100)  # Leer los primeros 100 bytes
            
        # Verificar que el contenido parece estar encriptado (no es texto plano)
        is_binary = lambda bytes: bool(bytes.translate(None, bytearray(range(32, 127))))
        assert is_binary(content), "El contenido del backup no parece estar encriptado"
    except Exception as e:
        pytest.fail(f"Error al verificar la encriptación del backup: {e}")

def test_backup_cleanup():
    """Probar la limpieza de backups antiguos"""
    try:
        # Crear un backup
        backup_info = backup_manager.backup_database()
        
        # Ejecutar limpieza
        deleted = backup_manager.cleanup_old_backups()
        
        # Verificar que la función se ejecutó sin errores
        assert isinstance(deleted, list), "La limpieza de backups no retornó una lista"
    except Exception as e:
        pytest.fail(f"Error al probar la limpieza de backups: {e}")

def test_logging_system():
    """Verificar que el sistema de logging funciona"""
    try:
        # Registrar un evento de prueba
        test_event = {
            'type': 'test_backup',
            'timestamp': datetime.now().isoformat()
        }
        security_logger.log_security_event('test_backup', test_event)
        
        # Verificar que el archivo de log existe y contiene datos
        log_file = Path(__file__).parent.parent / 'app' / 'logs' / 'security.log'
        assert log_file.exists(), "El archivo de log no existe"
        assert log_file.stat().st_size > 0, "El archivo de log está vacío"
    except Exception as e:
        pytest.fail(f"Error al probar el sistema de logging: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
