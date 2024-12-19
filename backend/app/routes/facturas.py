from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.factura import Factura
from ..schemas.factura import FacturaCreate, FacturaUpdate, FacturaResponse
from ..services.factura_service import FacturaService
from ..services.notification_service import NotificationService
from ..services.pdf_service import PDFGenerator
from ..services.signature_service import SignatureService
from ..auth import get_current_user
from ..models.usuario import Usuario

router = APIRouter(prefix="/facturas", tags=["facturas"])

@router.post("/", response_model=FacturaResponse)
async def crear_factura(
    factura: FacturaCreate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva factura.
    """
    factura_service = FacturaService(db)
    nueva_factura = factura_service.crear_factura(factura)
    return nueva_factura

@router.get("/", response_model=List[FacturaResponse])
async def listar_facturas(
    cliente_id: Optional[int] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar facturas con filtros opcionales.
    """
    factura_service = FacturaService(db)
    facturas = factura_service.obtener_facturas(cliente_id, estado)
    return facturas

@router.put("/{factura_id}", response_model=FacturaResponse)
async def actualizar_factura(
    factura_id: int,
    factura: FacturaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar una factura existente.
    """
    factura_service = FacturaService(db)
    factura_actualizada = factura_service.actualizar_factura(factura_id, factura)
    return factura_actualizada

@router.post("/{factura_id}/enviar", response_model=dict)
async def enviar_factura(
    factura_id: int,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Enviar una factura por email.
    """
    notification_service = NotificationService(
        config_path="config/notification_config.json"
    )
    factura_service = FacturaService(
        db, 
        notification_service=notification_service
    )
    
    try:
        enviada = await factura_service.enviar_factura_por_email(
            factura_id, 
            email
        )
        return {"success": enviada, "message": "Factura enviada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{factura_id}/firmar", response_model=FacturaResponse)
async def firmar_factura(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Firmar digitalmente una factura.
    """
    signature_service = SignatureService()
    factura_service = FacturaService(
        db, 
        signature_service=signature_service
    )
    
    try:
        factura_firmada = await factura_service.firmar_factura(factura_id)
        return factura_firmada
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
