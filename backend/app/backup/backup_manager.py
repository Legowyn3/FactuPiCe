import os
import shutil
import json
import gzip
import hashlib
from datetime import datetime
import subprocess
from typing import Dict, List, Optional
from ..logging.logger import security_logger
from dotenv import load_dotenv

load_dotenv()

class BackupManager:
    def __init__(self):
        # Configuración de directorios
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.backup_dir = os.path.join(self.base_dir, 'backups')
        self.temp_dir = os.path.join(self.backup_dir, 'temp')
        
        # Crear directorios si no existen
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Cargar configuración
        self.db_url = os.getenv('DATABASE_URL')
        self.backup_retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        self.encryption_key = os.getenv('BACKUP_ENCRYPTION_KEY')

    def _get_backup_filename(self, backup_type: str) -> str:
        """Generar nombre de archivo de backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{backup_type}_{timestamp}"

    def _calculate_checksum(self, file_path: str) -> str:
        """Calcular checksum SHA-256 de un archivo"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()

    def _compress_file(self, source_path: str, dest_path: str):
        """Comprimir archivo usando gzip"""
        with open(source_path, 'rb') as src, gzip.open(dest_path + '.gz', 'wb') as dst:
            shutil.copyfileobj(src, dst)

    def _encrypt_file(self, file_path: str):
        """Cifrar archivo usando gpg"""
        if not self.encryption_key:
            raise ValueError("No se ha configurado la clave de cifrado")
        
        output_path = file_path + '.gpg'
        cmd = [
            'gpg',
            '--batch',
            '--yes',
            '--passphrase', self.encryption_key,
            '--symmetric',
            '--cipher-algo', 'AES256',
            '--output', output_path,
            file_path
        ]
        
        subprocess.run(cmd, check=True)
        return output_path

    def backup_database(self) -> Dict:
        """Realizar backup de la base de datos"""
        try:
            # Generar nombre de archivo
            filename = self._get_backup_filename('db')
            temp_path = os.path.join(self.temp_dir, filename)
            final_path = os.path.join(self.backup_dir, filename)

            # Realizar dump de la base de datos
            if 'postgresql' in self.db_url:
                cmd = [
                    'pg_dump',
                    '-Fc',  # Formato personalizado
                    '-f', temp_path,
                    self.db_url
                ]
            else:
                raise ValueError("Tipo de base de datos no soportado")

            subprocess.run(cmd, check=True)

            # Comprimir
            self._compress_file(temp_path, final_path)
            compressed_path = final_path + '.gz'

            # Calcular checksum
            checksum = self._calculate_checksum(compressed_path)

            # Cifrar
            encrypted_path = self._encrypt_file(compressed_path)

            # Limpiar archivos temporales
            os.remove(temp_path)
            os.remove(compressed_path)

            # Registrar en el log
            backup_info = {
                'type': 'database',
                'filename': os.path.basename(encrypted_path),
                'timestamp': datetime.now().isoformat(),
                'checksum': checksum,
                'size': os.path.getsize(encrypted_path),
                'success': True,
                'file_path': encrypted_path
            }
            
            security_logger.log_security_event(
                'backup_created',
                backup_info
            )

            return backup_info

        except Exception as e:
            security_logger.log_incident(
                'backup_failed',
                {
                    'type': 'database',
                    'error': str(e)
                },
                'error'
            )
            raise

    def backup_logs(self) -> Dict:
        """Realizar backup de los logs"""
        try:
            # Generar nombre de archivo
            filename = self._get_backup_filename('logs')
            temp_path = os.path.join(self.temp_dir, filename)
            final_path = os.path.join(self.backup_dir, filename)
            
            # Crear archivo tar con los logs
            log_dir = os.path.join(self.base_dir, 'logs')
            cmd = [
                'tar',
                '-czf',
                temp_path,
                '-C', log_dir,
                '.'
            ]
            
            subprocess.run(cmd, check=True)
            
            # Calcular checksum
            checksum = self._calculate_checksum(temp_path)
            
            # Cifrar
            encrypted_path = self._encrypt_file(temp_path)
            
            # Limpiar archivo temporal
            os.remove(temp_path)
            
            # Registrar en el log
            backup_info = {
                'type': 'logs',
                'filename': os.path.basename(encrypted_path),
                'timestamp': datetime.now().isoformat(),
                'checksum': checksum,
                'size': os.path.getsize(encrypted_path),
                'success': True,
                'file_path': encrypted_path
            }
            
            security_logger.log_security_event(
                'backup_created',
                backup_info
            )
            
            return backup_info
            
        except Exception as e:
            security_logger.log_incident(
                'backup_failed',
                {
                    'type': 'logs',
                    'error': str(e)
                },
                'error'
            )
            raise

    def restore_database(self, backup_file: str) -> bool:
        """Restaurar backup de base de datos"""
        try:
            # Verificar que el archivo existe
            backup_path = os.path.join(self.backup_dir, backup_file)
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Archivo de backup no encontrado: {backup_file}")
            
            # Desencriptar
            temp_encrypted = os.path.join(self.temp_dir, 'temp_encrypted')
            shutil.copy(backup_path, temp_encrypted)
            
            cmd_decrypt = [
                'gpg',
                '--batch',
                '--yes',
                '--passphrase', self.encryption_key,
                '--decrypt',
                '--output', temp_encrypted + '.gz',
                temp_encrypted
            ]
            
            subprocess.run(cmd_decrypt, check=True)
            
            # Descomprimir
            with gzip.open(temp_encrypted + '.gz', 'rb') as f_in:
                with open(temp_encrypted + '.sql', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Restaurar base de datos
            if 'postgresql' in self.db_url:
                cmd_restore = [
                    'pg_restore',
                    '--clean',  # Limpiar BD antes de restaurar
                    '--if-exists',
                    '-d', self.db_url,
                    temp_encrypted + '.sql'
                ]
            else:
                raise ValueError("Tipo de base de datos no soportado")
            
            subprocess.run(cmd_restore, check=True)
            
            # Limpiar archivos temporales
            os.remove(temp_encrypted)
            os.remove(temp_encrypted + '.gz')
            os.remove(temp_encrypted + '.sql')
            
            # Registrar en el log
            security_logger.log_security_event(
                'backup_restored',
                {
                    'type': 'database',
                    'filename': backup_file,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            security_logger.log_incident(
                'restore_failed',
                {
                    'type': 'database',
                    'filename': backup_file,
                    'error': str(e)
                },
                'error'
            )
            raise

    def cleanup_old_backups(self) -> List[str]:
        """Limpiar backups antiguos según la política de retención"""
        try:
            deleted_files = []
            cutoff_date = datetime.now().timestamp() - (self.backup_retention_days * 24 * 60 * 60)
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_files.append(filename)
            
            if deleted_files:
                security_logger.log_security_event(
                    'backups_cleaned',
                    {'deleted_files': deleted_files}
                )
            
            return deleted_files
        
        except Exception as e:
            security_logger.log_incident(
                'backup_cleanup_failed',
                {
                    'error': str(e)
                },
                'error'
            )
            raise

    def list_backups(self) -> List[Dict]:
        """Listar todos los backups disponibles"""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('backup_') and filename.endswith('.gpg'):
                    file_path = os.path.join(self.backup_dir, filename)
                    backup_info = {
                        'filename': filename,
                        'timestamp': datetime.fromtimestamp(
                            os.path.getctime(file_path)
                        ).isoformat(),
                        'size': os.path.getsize(file_path)
                    }
                    backups.append(backup_info)
            
            return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            security_logger.log_incident(
                'backup_list_failed',
                {
                    'error': str(e)
                },
                'error'
            )
            raise

# Instancia global del gestor de backups
backup_manager = BackupManager()
