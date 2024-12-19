from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generar_factura_pdf(factura, output_dir="facturas_exportadas"):
    """
    Genera un archivo PDF para la factura proporcionada.
    
    Args:
        factura (dict): Datos de la factura.
        output_dir (str): Directorio donde se guardará el PDF.
    Returns:
        str: Ruta al archivo PDF generado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = f"factura_{factura['numero']}.pdf"
    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(100, 750, "Factura")
    c.drawString(100, 730, f"Fecha: {factura['fecha']}")
    c.drawString(100, 710, f"Número: {factura['numero']}")
    c.drawString(100, 690, f"NIF/CIF Cliente: {factura['nif_cif_cliente']}")
    c.drawString(100, 670, f"Base Imponible: {factura['base_imponible']:.2f} €")
    c.drawString(100, 650, f"Tipo IVA: {factura['tipo_iva']}%")
    c.drawString(100, 630, f"Cuota IVA: {factura['cuota_iva']:.2f} €")
    c.drawString(100, 610, f"Tipo Retención: {factura['tipo_retencion']}%")
    c.drawString(100, 590, f"Retención: {factura['retencion']:.2f} €")
    c.drawString(100, 570, f"Total Factura: {factura['total_factura']:.2f} €")
    c.drawString(100, 550, f"Concepto: {factura['concepto']}")
    c.drawString(100, 530, f"Estado: {factura['estado']}")

    c.showPage()
    c.save()

    return file_path
