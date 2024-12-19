import requests
from datetime import date

# Definir la URL del endpoint
url = "http://127.0.0.1:8000/facturas/"

# Crear los datos de la factura (en formato JSON)
data = {
    "fecha": str(date.today()),  # Fecha actual
    "numero": "FAC-001",
    "nif_cif_cliente": "B12345678",
    "base_imponible": 100.0,
    "tipo_iva": 21.0,
    "cuota_iva": 21.0,
    "tipo_retencion": 15.0,
    "retencion": 15.0,
    "total_factura": 106.0,
    "concepto_factura": "Servicios de consultoría",
    "estado_factura": "pendiente"
}

# Enviar la solicitud POST con los datos
response = requests.post(url, json=data)

# Verificar la respuesta
if response.status_code == 200:
    print("Factura creada correctamente:", response.json())
else:
    print("Error al crear la factura. Código de estado:", response.status_code)
