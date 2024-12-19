from app.utils.pdf_generator import generar_factura_pdf

# Datos de prueba para la factura
factura_data = {
    "fecha": "2024-12-12",
    "numero": "012",
    "nif_cif_cliente": "B12345678",
    "base_imponible": 2500.0,
    "tipo_iva": 21.0,
    "cuota_iva": 525.0,
    "tipo_retencion": 0.0,
    "retencion": 0.0,
    "total_factura": 3025.0,
    "concepto": "Servicios legales",
    "estado": "pendiente"
}

# Llama a la función y genera el PDF
generar_factura_pdf(factura_data)
print("PDF generado con éxito.")
