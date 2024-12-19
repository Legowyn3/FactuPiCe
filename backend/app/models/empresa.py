from sqlalchemy import Column, String, Integer
from .base import Base

class Empresa(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True)
    nif = Column(String(9), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=False)
    codigo_postal = Column(String(5), nullable=False)
    poblacion = Column(String(100), nullable=False)
    provincia = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Empresa(nif='{self.nif}', nombre='{self.nombre}')>"
