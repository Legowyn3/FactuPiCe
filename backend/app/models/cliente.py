from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nif_cif = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    nombre_comercial = Column(String, nullable=True)
    direccion = Column(String, nullable=False)
    codigo_postal = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    provincia = Column(String, nullable=False)
    pais = Column(String, nullable=False, default="España")
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Relación con facturas
    facturas = relationship("Factura", back_populates="cliente")
