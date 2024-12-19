from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from ..auth import get_current_active_user
from ..backup.backup_manager import backup_manager
from ..logging.logger import security_logger

router = APIRouter(
    prefix="/api/backup",
    tags=["backup"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/database")
async def create_database_backup() -> Dict:
    """Crear un nuevo backup de la base de datos"""
    try:
        backup_info = backup_manager.backup_database()
        return {"status": "success", "backup": backup_info}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear backup de base de datos: {str(e)}"
        )

@router.post("/logs")
async def create_logs_backup() -> Dict:
    """Crear un nuevo backup de los logs"""
    try:
        backup_info = backup_manager.backup_logs()
        return {"status": "success", "backup": backup_info}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear backup de logs: {str(e)}"
        )

@router.post("/restore/{filename}")
async def restore_backup(filename: str) -> Dict:
    """Restaurar un backup específico"""
    try:
        success = backup_manager.restore_database(filename)
        return {
            "status": "success" if success else "error",
            "message": "Backup restaurado correctamente" if success else "Error al restaurar backup"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al restaurar backup: {str(e)}"
        )

@router.get("/list")
async def list_backups() -> List[Dict]:
    """Listar todos los backups disponibles"""
    try:
        backups = backup_manager.list_backups()
        return backups
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar backups: {str(e)}"
        )

@router.post("/cleanup")
async def cleanup_old_backups() -> Dict:
    """Limpiar backups antiguos"""
    try:
        backup_manager.cleanup_old_backups()
        return {"status": "success", "message": "Limpieza de backups completada"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al limpiar backups antiguos: {str(e)}"
        )
