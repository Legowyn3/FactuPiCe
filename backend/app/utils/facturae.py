from datetime import datetime
import hashlib
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import pytz
from ..models.factura import Factura
from ..models.cliente import Cliente

class FacturaEGenerator:
    FACTURAE_VERSION = "3.2.2"
    SCHEMA_NS = "http://www.facturae.es/Facturae/2014/v3.2.2/Facturae"
    
    def __init__(self):
        ET.register_namespace("", self.SCHEMA_NS)
        self.timezone = pytz.timezone('Europe/Madrid')
        self.VERIFACTU_VERSION = "1.0"

    def generate_invoice_hash(self, factura: Factura) -> str:
        """Genera el hash de la factura según especificaciones AEAT."""
        datos = (
            f"{factura.serie}{factura.numero}"
            f"{factura.fecha_expedicion.isoformat()}"
            f"{factura.base_imponible:.2f}"
            f"{factura.total_factura:.2f}"
        )
        return hashlib.sha256(datos.encode()).hexdigest()

    def generate_tbai_id(self, factura: Factura) -> str:
        """Genera el identificador único TBAI."""
        return f"TBAI-{factura.serie}-{factura.numero}-{self.generate_invoice_hash(factura)[:8]}"

    def generate_xml(self, factura: Factura, cliente: Cliente, software_info: Dict) -> ET.Element:
        """Genera el XML de la factura en formato FacturaE."""
        root = ET.Element("{%s}Facturae" % self.SCHEMA_NS)
        
        # Cabecera
        header = ET.SubElement(root, "FileHeader")
        ET.SubElement(header, "SchemaVersion").text = self.FACTURAE_VERSION
        ET.SubElement(header, "Modality").text = "I"
        
        # Información del software
        software = ET.SubElement(header, "SoftwareInfo")
        ET.SubElement(software, "SoftwareName").text = software_info['name']
        ET.SubElement(software, "SoftwareVersion").text = software_info['version']
        ET.SubElement(software, "SoftwareLicense").text = software_info['license']
        
        # Información de la factura
        invoices = ET.SubElement(root, "Invoices")
        invoice = ET.SubElement(invoices, "Invoice")
        
        # Datos de la factura
        invoice_header = ET.SubElement(invoice, "InvoiceHeader")
        ET.SubElement(invoice_header, "InvoiceNumber").text = factura.numero
        ET.SubElement(invoice_header, "InvoiceSeriesCode").text = factura.serie
        ET.SubElement(invoice_header, "InvoiceDocumentType").text = "FC" if factura.tipo == "ordinaria" else "FR"
        
        # Fechas
        invoice_issue_data = ET.SubElement(invoice, "InvoiceIssueData")
        ET.SubElement(invoice_issue_data, "IssueDate").text = factura.fecha_expedicion.strftime("%Y-%m-%d")
        if factura.fecha_operacion:
            ET.SubElement(invoice_issue_data, "OperationDate").text = factura.fecha_operacion.strftime("%Y-%m-%d")
        
        # Importes
        tax_data = ET.SubElement(invoice, "TaxesOutputs")
        tax = ET.SubElement(tax_data, "Tax")
        ET.SubElement(tax, "TaxTypeCode").text = "01"  # IVA
        ET.SubElement(tax, "TaxRate").text = str(factura.tipo_iva)
        ET.SubElement(tax, "TaxableBase").text = f"{factura.base_imponible:.2f}"
        ET.SubElement(tax, "TaxAmount").text = f"{factura.cuota_iva:.2f}"
        
        # Retenciones si aplican
        if factura.tipo_retencion:
            withholding = ET.SubElement(invoice, "WithholdingTax")
            ET.SubElement(withholding, "WithholdingRate").text = str(factura.tipo_retencion)
            ET.SubElement(withholding, "WithholdingAmount").text = f"{factura.retencion:.2f}"
        
        # Totales
        amounts = ET.SubElement(invoice, "InvoiceTotals")
        ET.SubElement(amounts, "TotalGrossAmount").text = f"{factura.total_factura:.2f}"
        ET.SubElement(amounts, "TotalTaxOutputs").text = f"{factura.cuota_iva:.2f}"
        if factura.retencion:
            ET.SubElement(amounts, "TotalWithholdingAmount").text = f"{factura.retencion:.2f}"
        ET.SubElement(amounts, "InvoiceTotal").text = f"{factura.total_factura:.2f}"
        
        # Información TBAI
        tbai = ET.SubElement(invoice, "TBAIInfo")
        ET.SubElement(tbai, "TBAIIdentifier").text = self.generate_tbai_id(factura)
        ET.SubElement(tbai, "PreviousInvoiceHash").text = ""  # Debe implementarse la lógica para obtener el hash anterior
        
        self.add_verifactu_elements(root, factura)
        
        return root

    def generate_qr(self, factura: Factura) -> str:
        """Genera el código QR según especificaciones AEAT."""
        qr_data = {
            "tbai": self.generate_tbai_id(factura),
            "nif_emisor": factura.cliente.nif_cif,
            "fecha": factura.fecha_expedicion.strftime("%Y-%m-%d"),
            "base": f"{factura.base_imponible:.2f}",
            "cuota": f"{factura.cuota_iva:.2f}",
            "total": f"{factura.total_factura:.2f}",
            "hash": self.generate_invoice_hash(factura)
        }
        
        # Formato específico para QR según AEAT
        qr_string = "&".join([f"{k}={v}" for k, v in qr_data.items()])
        return qr_string  # Este string debe ser convertido a QR usando una librería específica

    def add_verifactu_elements(self, root: ET.Element, factura: Factura) -> None:
        """Añade elementos específicos de VERI*FACTU"""
        verifactu = ET.SubElement(root, "VERIFACTUInfo")
        ET.SubElement(verifactu, "Version").text = self.VERIFACTU_VERSION
        ET.SubElement(verifactu, "Marca").text = "VERI*FACTU"
        ET.SubElement(verifactu, "FechaExpedicion").text = factura.fecha_expedicion.isoformat()
