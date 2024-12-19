import os
import shutil
from datetime import datetime
import subprocess
from pathlib import Path
import logging
from typing import List
import schedule
import time
import threading

class BackupManager:
    def __init__(self):
        self.logger = logging.getLogger('backup')
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        handler = logging.FileHandler('logs/backup.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _create_backup_name(self) -> str:
        """Genera un nombre único para el backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{timestamp}"

    def backup_database(self) -> bool:
        """Realiza backup de la base de datos."""
        try:
            backup_name = self._create_backup_name()
            backup_path = self.backup_dir / f"{backup_name}.sql"
            
            # Obtener credenciales de la base de datos desde variables de entorno
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                self.logger.error("DATABASE_URL no está configurada")
                return False
            
            # Ejecutar pg_dump
            result = subprocess.run([
                'pg_dump',
                '-h', 'localhost',
                '-U', 'myuser',
                '-d', 'facturas',
                '-f', str(backup_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Error en backup de BD: {result.stderr}")
                return False
            
            self.logger.info(f"Backup de BD creado: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error durante el backup de BD: {str(e)}")
            return False

    def backup_files(self) -> bool:
        """Realiza backup de archivos importantes."""
        try:
            backup_name = self._create_backup_name()
            backup_path = self.backup_dir / f"{backup_name}_files"
            
            # Directorios a respaldar
            dirs_to_backup = [
                'app',
                'alembic',
                'scripts',
                'logs'
            ]
            
            # Crear directorio de backup
            backup_path.mkdir(exist_ok=True)
            
            # Copiar directorios
            for dir_name in dirs_to_backup:
                src = Path(dir_name)
                if src.exists():
                    dst = backup_path / dir_name
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            
            self.logger.info(f"Backup de archivos creado: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error durante el backup de archivos: {str(e)}")
            return False

    def cleanup_old_backups(self, keep_days: int = 30):
        """Elimina backups antiguos."""
        try:
            current_time = datetime.now()
            for backup_file in self.backup_dir.glob('*'):
                if backup_file.is_file() or backup_file.is_dir():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if (current_time - file_time).days > keep_days:
                        if backup_file.is_file():
                            backup_file.unlink()
                        else:
                            shutil.rmtree(backup_file)
                        self.logger.info(f"Backup antiguo eliminado: {backup_file}")
                        
        except Exception as e:
            self.logger.error(f"Error durante la limpieza de backups: {str(e)}")

    def schedule_backups(self):
        """Programa backups automáticos."""
        schedule.every().day.at("02:00").do(self.backup_database)
        schedule.every().day.at("03:00").do(self.backup_files)
        schedule.every().week.do(lambda: self.cleanup_old_backups(30))
        
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        # Iniciar el planificador en un hilo separado
        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()

backup_manager = BackupManager()
