import os
import sys
from datetime import datetime
import schedule
import time
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path de Python
sys.path.append(str(Path(__file__).parent.parent))

from app.backup.backup_manager import backup_manager
from app.logging.logger import security_logger

load_dotenv()

def perform_database_backup():
    """Realizar backup de la base de datos"""
    try:
        backup_info = backup_manager.backup_database()
        security_logger.log_security_event(
            'scheduled_backup_completed',
            {
                'type': 'database',
                'backup_info': backup_info
            }
        )
    except Exception as e:
        security_logger.log_incident(
            'scheduled_backup_failed',
            {
                'type': 'database',
                'error': str(e)
            },
            'error'
        )

def perform_logs_backup():
    """Realizar backup de los logs"""
    try:
        backup_info = backup_manager.backup_logs()
        security_logger.log_security_event(
            'scheduled_backup_completed',
            {
                'type': 'logs',
                'backup_info': backup_info
            }
        )
    except Exception as e:
        security_logger.log_incident(
            'scheduled_backup_failed',
            {
                'type': 'logs',
                'error': str(e)
            },
            'error'
        )

def cleanup_old_backups():
    """Limpiar backups antiguos"""
    try:
        backup_manager.cleanup_old_backups()
        security_logger.log_security_event(
            'backup_cleanup_completed',
            {
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        security_logger.log_incident(
            'backup_cleanup_failed',
            {
                'error': str(e)
            },
            'error'
        )

def main():
    """Configurar y ejecutar el programador de backups"""
    print("Iniciando programador de backups...")
    
    # Programar backup diario de la base de datos a las 2 AM
    schedule.every().day.at("02:00").do(perform_database_backup)
    print("✓ Backup de base de datos programado para las 2:00 AM")
    
    # Programar backup diario de logs a las 3 AM
    schedule.every().day.at("03:00").do(perform_logs_backup)
    print("✓ Backup de logs programado para las 3:00 AM")
    
    # Programar limpieza de backups antiguos a las 4 AM
    schedule.every().day.at("04:00").do(cleanup_old_backups)
    print("✓ Limpieza de backups antiguos programada para las 4:00 AM")
    
    print("\nEjecutando programador de backups...")
    print("Presiona Ctrl+C para detener")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Esperar 1 minuto entre verificaciones
    except KeyboardInterrupt:
        print("\nProgramador de backups detenido")

if __name__ == "__main__":
    main()
