from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from typing import Dict, Any

class PDFGenerator:
    def __init__(self, output_dir: str = "facturas_exportadas"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate(self, factura_data: Dict[str, Any]) -> str:
        """
        Genera un PDF para la factura
        """
        file_name = f"factura_{factura_data['numero']}.pdf"
        file_path = os.path.join(self.output_dir, file_name)
        
        c = canvas.Canvas(file_path, pagesize=letter)
        # Aquí iría la lógica de generación del PDF
        c.save()
        
        return file_path 