from datetime import datetime
from typing import Dict, Optional
from lxml import etree
from ..utils.aeat_errors import ValidationError, SignatureError
from .signature_service import SignatureService
from .qr_service import QRService
from ..models.factura import Factura

class TicketBAIService:
    def __init__(self, signature_service: SignatureService, qr_service: QRService):
        """
        Inicializa el servicio TicketBAI.
        
        Args:
            signature_service: Servicio de firma
            qr_service: Servicio QR
        """
        self.signature_service = signature_service
        self.qr_service = qr_service
        self.api_url = "https://pruebas-ticketbai.araba.eus/TicketBAI/v1"

    def generar_xml_factura(self, factura: Factura) -> str:
        """
        Genera el XML de una factura.
        
        Args:
            factura: Datos de la factura
            
        Returns:
            str: XML generado
        """
        try:
            # Validar la factura
            self.validar_factura(factura)
            
            # Crear el elemento raíz
            root = etree.Element("TicketBai")
            
            # Cabecera
            cabecera = etree.SubElement(root, "Cabecera")
            etree.SubElement(cabecera, "IDVersionTBAI").text = "1.2"
            
            # Datos factura
            datos_factura = etree.SubElement(root, "Factura")
            etree.SubElement(datos_factura, "Serie").text = factura.serie
            etree.SubElement(datos_factura, "NumFactura").text = factura.numero
            etree.SubElement(datos_factura, "FechaExpedicion").text = factura.fecha.strftime("%Y-%m-%d")
            
            # Datos emisor
            emisor = etree.SubElement(datos_factura, "Emisor")
            etree.SubElement(emisor, "NIF").text = factura.empresa_emisora.nif
            etree.SubElement(emisor, "ApellidosNombreRazonSocial").text = factura.empresa_emisora.nombre
            
            # Datos destinatario
            destinatario = etree.SubElement(datos_factura, "Destinatario")
            etree.SubElement(destinatario, "NIF").text = factura.nif_cliente
            etree.SubElement(destinatario, "ApellidosNombreRazonSocial").text = factura.nombre_cliente
            
            # Detalles factura
            detalles = etree.SubElement(datos_factura, "DetallesFactura")
            for detalle in factura.detalles:
                linea = etree.SubElement(detalles, "LineaFactura")
                etree.SubElement(linea, "Descripcion").text = detalle.descripcion
                etree.SubElement(linea, "Cantidad").text = str(detalle.cantidad)
                etree.SubElement(linea, "ImporteUnitario").text = str(detalle.precio_unitario)
                etree.SubElement(linea, "TipoIVA").text = str(detalle.tipo_iva)
            
            # Importes
            importes = etree.SubElement(datos_factura, "Importes")
            etree.SubElement(importes, "BaseImponible").text = str(factura.base_imponible)
            etree.SubElement(importes, "CuotaIVA").text = str(factura.cuota_iva)
            etree.SubElement(importes, "ImporteTotal").text = str(factura.total)
            
            return etree.tostring(root, encoding='unicode', pretty_print=True)
            
        except Exception as e:
            raise ValidationError(f"Error al generar el XML: {str(e)}")

    def firmar_factura(self, xml: str) -> str:
        """
        Firma el XML de una factura.
        
        Args:
            xml: XML a firmar
            
        Returns:
            str: XML firmado
        """
        try:
            return self.signature_service.sign_xml(xml)
        except Exception as e:
            raise SignatureError(f"Error al firmar la factura: {str(e)}")

    def generar_qr(self, xml_firmado: str) -> bytes:
        """
        Genera el código QR para una factura.
        
        Args:
            xml_firmado: XML firmado de la factura
            
        Returns:
            bytes: Imagen del código QR
        """
        try:
            # Calcular el identificador único
            identificador = self._calcular_identificador(xml_firmado)
            
            # Generar la URL de verificación
            url = f"{self.api_url}/verificar/{identificador}"
            
            # Generar el código QR
            return self.qr_service.generate_qr_code(url)
            
        except Exception as e:
            raise ValidationError(f"Error al generar el código QR: {str(e)}")

    def procesar_factura(self, factura: Factura) -> Dict:
        """
        Procesa una factura completa.
        
        Args:
            factura: Datos de la factura
            
        Returns:
            Dict: Resultado del procesamiento
        """
        try:
            # Generar XML
            xml = self.generar_xml_factura(factura)
            
            # Firmar XML
            xml_firmado = self.firmar_factura(xml)
            
            # Generar QR
            qr_code = self.generar_qr(xml_firmado)
            
            return {
                "xml_firmado": xml_firmado,
                "qr_code": qr_code
            }
            
        except Exception as e:
            raise ValidationError(f"Error al procesar la factura: {str(e)}")

    def validar_factura(self, factura: Factura) -> bool:
        """
        Valida los datos de una factura.
        
        Args:
            factura: Factura a validar
            
        Returns:
            bool: True si la factura es válida
        """
        if not factura.serie or not factura.numero:
            raise ValidationError("La serie y número de factura son obligatorios")
            
        if not factura.empresa_emisora:
            raise ValidationError("Los datos de la empresa emisora son obligatorios")
            
        if not factura.nif_cliente or not factura.nombre_cliente:
            raise ValidationError("Los datos del cliente son obligatorios")
            
        if not factura.detalles:
            raise ValidationError("La factura debe tener al menos un detalle")
            
        if factura.total <= 0:
            raise ValidationError("El importe total debe ser mayor que cero")
            
        return True

    def enviar_factura(self, xml_firmado: str, qr_code: bytes) -> Dict:
        """
        Envía una factura al servicio TicketBAI.
        
        Args:
            xml_firmado: XML firmado de la factura
            qr_code: Código QR de la factura
            
        Returns:
            Dict: Respuesta del servicio
        """
        # Simulación de envío
        return {
            "estado": "ACEPTADA",
            "identificador": self._calcular_identificador(xml_firmado)
        }

    def consultar_estado(self, identificador: str) -> Dict:
        """
        Consulta el estado de una factura.
        
        Args:
            identificador: Identificador de la factura
            
        Returns:
            Dict: Estado de la factura
        """
        # Simulación de consulta
        return {
            "estado": "ACEPTADA",
            "fecha_procesamiento": datetime.now().isoformat()
        }

    def _calcular_identificador(self, xml_firmado: str) -> str:
        """
        Calcula el identificador único de una factura.
        
        Args:
            xml_firmado: XML firmado de la factura
            
        Returns:
            str: Identificador único
        """
        import hashlib
        return hashlib.sha256(xml_firmado.encode()).hexdigest()[:20]
