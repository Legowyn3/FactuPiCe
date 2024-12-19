import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def create_directories():
    """Crear directorios necesarios"""
    print("\nCreando directorios...")
    
    base_dir = Path(__file__).parent.parent
    dirs = [
        base_dir / 'app' / 'logs',
        base_dir / 'app' / 'backups',
        base_dir / 'app' / 'backups' / 'temp'
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado: {dir_path}")
    
    # Establecer permisos seguros
    for dir_path in dirs:
        os.chmod(dir_path, 0o700)  # Solo el propietario puede leer/escribir/ejecutar
        print(f"✓ Permisos establecidos para: {dir_path}")

def check_dependencies():
    """Verificar dependencias del sistema"""
    print("\nVerificando dependencias...")
    
    dependencies = {
        'gpg': 'gnupg',
        'pg_dump': 'postgresql-client'
    }
    
    missing = []
    for cmd, pkg in dependencies.items():
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
            print(f"✓ {cmd} está instalado")
        except subprocess.CalledProcessError:
            print(f"✗ {cmd} no está instalado")
            missing.append(pkg)
    
    if missing:
        print(f"\nInstala las dependencias faltantes con:")
        print(f"sudo apt-get install {' '.join(missing)}")
        return False
    return True

def verify_env_variables():
    """Verificar variables de entorno requeridas"""
    print("\nVerificando variables de entorno...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'BACKUP_ENCRYPTION_KEY',
        'ALLOWED_ORIGINS'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            print(f"✗ {var} no está configurada")
            missing.append(var)
        else:
            print(f"✓ {var} está configurada")
    
    return len(missing) == 0

def setup_database():
    """Configurar la base de datos"""
    print("\nConfigurando base de datos...")
    
    try:
        # Importar aquí para evitar problemas si no está instalado
        from app.database import Base, engine
        
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas en la base de datos")
        return True
    except Exception as e:
        print(f"✗ Error al configurar la base de datos: {e}")
        return False

def test_security_features():
    """Probar características de seguridad"""
    print("\nProbando características de seguridad...")
    
    try:
        # Ejecutar los tests de seguridad
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'scripts/test_full_security.py', '-v'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Tests de seguridad completados exitosamente")
            return True
        else:
            print("✗ Algunos tests de seguridad fallaron:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"✗ Error al ejecutar los tests: {e}")
        return False

def main():
    """Función principal de configuración"""
    print("=== Iniciando configuración del sistema de seguridad ===")
    
    # Lista de pasos de configuración
    steps = [
        ("Crear directorios", create_directories),
        ("Verificar dependencias", check_dependencies),
        ("Verificar variables de entorno", verify_env_variables),
        ("Configurar base de datos", setup_database),
        ("Configurar GPG", lambda: __import__('setup_gpg').setup_gpg()),
        ("Probar características de seguridad", test_security_features)
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n=== {step_name} ===")
        if not step_func():
            print(f"\n✗ Error en el paso: {step_name}")
            success = False
            break
        print(f"✓ {step_name} completado")
    
    if success:
        print("\n✅ Configuración completada exitosamente")
    else:
        print("\n❌ La configuración no se completó correctamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
