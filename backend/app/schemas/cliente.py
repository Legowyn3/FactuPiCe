from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from .base_schemas import ClienteBase

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    nombre_comercial: Optional[str] = None
    direccion: Optional[str] = None
    codigo_postal: Optional[str] = Field(None, pattern=r'^\d{5}$')
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    pais: Optional[str] = None
    telefono: Optional[str] = Field(None, pattern=r'^\+?[0-9]{9,15}$')
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None

    class Config:
        from_attributes = True

class ClienteSimple(ClienteBase):
    id: int
    activo: bool

    class Config:
        from_attributes = True

class FacturaSimple(BaseModel):
    id: int
    numero: str
    estado: str

    class Config:
        from_attributes = True

class ClienteOut(ClienteSimple):
    facturas: List[FacturaSimple] = []

    class Config:
        from_attributes = True
