from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.factura import Factura
from ..schemas.factura import FacturaCreate, FacturaUpdate, FacturaOut
from ..services.facturae_service import FacturaEService
from ..services.security_service import SecurityService
from ..services.ticketbai_service import TicketBAIService
from ..services.audit_service import AuditService
from ..services.pdf_service import PDFGenerator
from ..auth import get_current_user
from ..models.user import User
from fastapi.responses import Response

router = APIRouter(prefix="/api/facturas", tags=["facturas"])

# Inicializar servicios
security_service = SecurityService()
ticketbai_service = TicketBAIService(security_service)
audit_service = AuditService("logs")  # Asegúrate de que este directorio existe
pdf_generator = PDFGenerator()

@router.post("/", response_model=FacturaOut)
async def create_factura(
    factura: FacturaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una nueva factura y la registra en TicketBAI."""
    try:
        # Crear la factura en la base de datos
        db_factura = Factura(**factura.dict())
        db.add(db_factura)
        db.flush()  # Para obtener el ID

        # Generar XML y firma
        facturae_service = FacturaEService()
        xml_content = await facturae_service.generate_invoice_xml(db_factura)
        signed_xml, timestamp = await security_service.sign_invoice_xml(xml_content)

        # Actualizar factura con XML y firma
        db_factura.xml_content = xml_content
        db_factura.signature = signed_xml
        db_factura.timestamp = timestamp

        # Enviar a TicketBAI
        tbai_result = await ticketbai_service.submit_invoice(db_factura)
        
        if not tbai_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Error en TicketBAI: {tbai_result['error']}"
            )

        # Registrar operación
        await audit_service.log_invoice_operation(
            db,
            "create",
            db_factura,
            tbai_result,
            current_user.id
        )

        db.commit()
        return db_factura

    except Exception as e:
        db.rollback()
        await audit_service.log_invoice_operation(
            db,
            "create_error",
            db_factura,
            {"success": False, "error": str(e)},
            current_user.id
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[FacturaOut])
async def list_facturas(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista las facturas con filtros opcionales."""
    query = db.query(Factura)
    
    if estado:
        query = query.filter(Factura.estado == estado)
    if fecha_inicio:
        query = query.filter(Factura.fecha_expedicion >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Factura.fecha_expedicion <= fecha_fin)
    
    facturas = query.offset(skip).limit(limit).all()
    return facturas

@router.get("/{factura_id}", response_model=FacturaOut)
async def get_factura(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una factura específica."""
    factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

@router.put("/{factura_id}", response_model=FacturaOut)
async def update_factura(
    factura_id: int,
    factura_update: FacturaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza una factura existente."""
    db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # Solo permitir actualización si está en borrador
    if db_factura.estado != "borrador":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden modificar facturas en estado borrador"
        )

    try:
        # Actualizar campos
        for field, value in factura_update.dict(exclude_unset=True).items():
            setattr(db_factura, field, value)

        # Si la factura está lista para emitir
        if factura_update.estado == "emitida":
            # Generar XML y firma
            facturae_service = FacturaEService()
            xml_content = await facturae_service.generate_invoice_xml(db_factura)
            signed_xml, timestamp = await security_service.sign_invoice_xml(xml_content)

            # Actualizar factura
            db_factura.xml_content = xml_content
            db_factura.signature = signed_xml
            db_factura.timestamp = timestamp

            # Enviar a TicketBAI
            tbai_result = await ticketbai_service.submit_invoice(db_factura)
            
            if not tbai_result['success']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error en TicketBAI: {tbai_result['error']}"
                )

        # Registrar operación
        await audit_service.log_invoice_operation(
            db,
            "update",
            db_factura,
            {"success": True},
            current_user.id
        )

        db.commit()
        return db_factura

    except Exception as e:
        db.rollback()
        await audit_service.log_invoice_operation(
            db,
            "update_error",
            db_factura,
            {"success": False, "error": str(e)},
            current_user.id
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{factura_id}")
async def delete_factura(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Anula una factura en TicketBAI."""
    db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    try:
        # Solo permitir anulación de facturas emitidas
        if db_factura.estado != "emitida":
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden anular facturas emitidas"
            )

        # Anular en TicketBAI
        cancel_result = await ticketbai_service.cancel_invoice(db_factura)
        
        if not cancel_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Error al anular en TicketBAI: {cancel_result['error']}"
            )

        # Cambiar estado de la factura
        db_factura.estado = "anulada"

        # Registrar operación
        await audit_service.log_invoice_operation(
            db,
            "cancel",
            db_factura,
            cancel_result,
            current_user.id
        )

        db.commit()
        return {"message": "Factura anulada con éxito"}

    except Exception as e:
        db.rollback()
        await audit_service.log_invoice_operation(
            db,
            "cancel_error",
            db_factura,
            {"success": False, "error": str(e)},
            current_user.id
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{factura_id}/history", response_model=List[dict])
async def get_factura_history(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el historial de una factura."""
    db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    history = await audit_service.get_invoice_history(db, factura_id)
    return history

@router.get("/{factura_id}/status")
async def check_factura_status(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consulta el estado de una factura en TicketBAI."""
    db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    status = await ticketbai_service.check_invoice_status(db_factura)
    return status

@router.get("/{factura_id}/download")
async def download_factura(
    factura_id: int,
    format: str = Query(..., regex="^(pdf|xml)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Descarga una factura en formato PDF o XML."""
    db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
    if not db_factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    try:
        if format == "xml":
            if not db_factura.xml_content:
                raise HTTPException(
                    status_code=400,
                    detail="XML no disponible para esta factura"
                )
            return Response(
                content=db_factura.xml_content,
                media_type="application/xml",
                headers={
                    "Content-Disposition": f"attachment; filename=factura_{factura_id}.xml"
                }
            )
        else:
            # Generar PDF
            pdf_content = await pdf_generator.generate_pdf(db_factura)
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=factura_{factura_id}.pdf"
                }
            )

    except Exception as e:
        await audit_service.log_invoice_operation(
            db,
            "download_error",
            db_factura,
            {"success": False, "error": str(e)},
            current_user.id
        )
        raise HTTPException(status_code=400, detail=str(e))
