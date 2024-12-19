from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Cliente, Usuario
from ..schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from .. import auth
from sqlalchemy import or_
import traceback

router = APIRouter(prefix="/api")

@router.post("/clientes", response_model=ClienteOut)
def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    try:
        # Verificar si ya existe un cliente con el mismo NIF/CIF
        db_cliente = db.query(Cliente).filter(Cliente.nif_cif == cliente.nif_cif).first()
        if db_cliente:
            raise HTTPException(status_code=400, detail="Ya existe un cliente con este NIF/CIF")
        
        # Crear el nuevo cliente
        cliente_dict = cliente.dict()
        print(f"Datos del cliente: {cliente_dict}")  # Debug
        db_cliente = Cliente(**cliente_dict)
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al crear cliente: {str(e)}")  # Debug
        traceback.print_exc()  # Debug
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(e)}")

@router.get("/clientes", response_model=List[ClienteOut])
def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    buscar: Optional[str] = Query(None, description="Buscar por nombre, NIF/CIF o email"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    try:
        query = db.query(Cliente)
        print(f"Query base: {query}")  # Debug
        
        # Aplicar filtro de búsqueda
        if buscar:
            buscar = f"%{buscar}%"
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(buscar),
                    Cliente.nif_cif.ilike(buscar),
                    Cliente.email.ilike(buscar) if Cliente.email else False
                )
            )
            print(f"Query con búsqueda: {query}")  # Debug
        
        # Aplicar filtro de estado activo
        if activo is not None:
            query = query.filter(Cliente.activo == activo)
            print(f"Query con filtro activo: {query}")  # Debug
        
        # Aplicar paginación
        clientes = query.offset(skip).limit(limit).all()
        print(f"Clientes encontrados: {len(clientes)}")  # Debug
        for cliente in clientes:
            print(f"  - ID: {cliente.id}, NIF/CIF: {cliente.nif_cif}, Nombre: {cliente.nombre}")  # Debug
        
        return clientes
    except Exception as e:
        print(f"Error al listar clientes: {str(e)}")  # Debug
        import traceback
        traceback.print_exc()  # Debug
        raise HTTPException(status_code=500, detail=f"Error al listar clientes: {str(e)}")

@router.get("/clientes/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.put("/clientes/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(
    cliente_id: int,
    cliente: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth.get_current_active_user)
):
    try:
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if db_cliente is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Actualizar solo los campos proporcionados
        cliente_data = cliente.dict(exclude_unset=True)
        for key, value in cliente_data.items():
            setattr(db_cliente, key, value)
        
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al actualizar cliente: {str(e)}")  # Debug
        traceback.print_exc()  # Debug
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(e)}")

@router.delete("/clientes/{cliente_id}")
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(auth.verify_admin)  # Solo administradores pueden eliminar
):
    try:
        db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if db_cliente is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Implementar borrado lógico
        db_cliente.activo = False
        db.commit()
        
        return {"message": "Cliente desactivado correctamente"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al eliminar cliente: {str(e)}")  # Debug
        traceback.print_exc()  # Debug
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(e)}")
