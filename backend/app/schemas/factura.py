from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class DetalleFacturaBase(BaseModel):
    concepto: str = Field(min_length=1, max_length=200)
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal = Field(gt=0)
    iva: int = Field(ge=0, le=21)

class DetalleFacturaCreate(DetalleFacturaBase):
    pass

class DetalleFactura(DetalleFacturaBase):
    id: int
    factura_id: int
    subtotal: Decimal
    iva_importe: Decimal
    total: Decimal

    class Config:
        from_attributes = True

class FacturaBase(BaseModel):
    cliente_id: int
    numero: str
    fecha_emision: datetime
    fecha_vencimiento: datetime
    notas: Optional[str] = None

class FacturaCreate(FacturaBase):
    detalles: List[DetalleFacturaCreate]

class Factura(FacturaBase):
    id: int
    usuario_id: int
    base_imponible: Decimal
    iva_total: Decimal
    total: Decimal
    estado: str
    detalles: List[DetalleFactura]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
