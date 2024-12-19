from sqlalchemy import Column, Integer, String, Float, Numeric, Enum, Date, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum
from datetime import datetime

class TipoFactura(enum.Enum):
    ordinaria = "ordinaria"
    rectificativa = "rectificativa"
    simplificada = "simplificada"
    recapitulativa = "recapitulativa"

class EstadoFactura(enum.Enum):
    borrador = "borrador"
    emitida = "emitida"
    pagada = "pagada"
    vencida = "vencida"
    cancelada = "cancelada"

class DetalleFactura(Base):
    __tablename__ = 'detalles_factura'

    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey('facturas.id'))
    descripcion = Column(String(200), nullable=False)
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    tipo_iva = Column(Float, nullable=False)

    def __repr__(self):
        return f"<DetalleFactura(descripcion='{self.descripcion}', cantidad={self.cantidad})>"

class Factura(Base):
    __tablename__ = "facturas"

    # Campos de identificación
    id = Column(Integer, primary_key=True, index=True)
    serie = Column(String(4), nullable=False)  # Serie de la factura (ej: "FACT", "RECT", "SIMP")
    numero = Column(String, unique=True, nullable=False)  # Número completo (serie + número)
    
    # Fechas
    fecha_expedicion = Column(DateTime, nullable=False)  # Fecha y hora de emisión
    fecha_operacion = Column(Date, nullable=True)  # Fecha de la operación si es diferente
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    
    # Importes y cálculos
    base_imponible = Column(Numeric(10, 2), nullable=False)  # Cambiado a Numeric para precisión
    tipo_iva = Column(Float, nullable=False)
    cuota_iva = Column(Numeric(10, 2), nullable=False)
    tipo_retencion = Column(Float, nullable=True)
    retencion = Column(Numeric(10, 2), nullable=True)
    total_factura = Column(Numeric(10, 2), nullable=False)
    
    # Detalles de la operación
    concepto = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)  # Descripción detallada de bienes/servicios
    
    # Clasificación y estado
    tipo = Column(Enum(TipoFactura), nullable=False, default=TipoFactura.ordinaria)
    estado = Column(Enum(EstadoFactura), nullable=False, default=EstadoFactura.borrador)
    
    # Referencias a otras facturas
    factura_original_id = Column(Integer, ForeignKey('facturas.id'), nullable=True)  # Para rectificativas
    
    # Campos para requisitos específicos
    motivo_rectificacion = Column(Text, nullable=True)  # Obligatorio para rectificativas
    periodo_recapitulativo = Column(String, nullable=True)  # Para facturas recapitulativas
    
    # Campos técnicos y de control
    fecha_vencimiento = Column(Date, nullable=True)
    metodo_pago = Column(String, nullable=True)
    cuenta_bancaria = Column(String, nullable=True)
    archivo_adjunto = Column(Text, nullable=True)  # Para PDF generado
    notas = Column(Text, nullable=True)
    firma_digital = Column(Text, nullable=True)  # Para facturas electrónicas
    
    # Campos para TicketBAI/FacturaE
    tbai_identifier = Column(String, nullable=True, unique=True)  # Identificador único TBAI
    previous_invoice_hash = Column(String, nullable=True)  # Hash de la factura anterior
    invoice_hash = Column(String, nullable=True)  # Hash de la factura actual
    qr_code = Column(Text, nullable=True)  # Código QR para verificación
    xml_content = Column(Text, nullable=True)  # Contenido XML de la factura
    signature = Column(Text, nullable=True)  # Firma XAdES
    timestamp = Column(DateTime, nullable=True)  # Timestamp de la firma
    
    # Campos de trazabilidad fiscal
    software_name = Column(String, nullable=False, default="InvoiceManager")
    software_version = Column(String, nullable=False, default="1.0.0")
    software_license = Column(String, nullable=False, default="GPL-3.0")
    
    # Nuevos campos de auditoría y fiscales
    hash_fiscal = Column(String(64), nullable=True)  # Hash fiscal único
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Nuevos campos para VERI*FACTU
    verifactu_version = Column(String, nullable=False, default="1.0")
    verifactu_timestamp = Column(DateTime(timezone=True), nullable=True)
    verifactu_validation_code = Column(String, nullable=True)

    # Método para soft delete
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()

    # Método para restaurar
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None

    # Relaciones
    cliente = relationship("Cliente", back_populates="facturas")
    factura_original = relationship("Factura", remote_side=[id])  # Para facturas rectificativas
    detalles = relationship("DetalleFactura", backref="factura")

    def __repr__(self):
        return f"<Factura(serie='{self.serie}', numero='{self.numero}', total={self.total_factura})>"
