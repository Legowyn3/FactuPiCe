import requests

BASE_URL = "http://127.0.0.1:8000/facturas/"

# Crear una factura
def test_create_factura():
    print("=== TEST: Crear Factura ===")
    data = {
        "fecha": "2024-12-11",
        "numero": "009",  # Asegúrate de usar un número único
        "nif_cif_cliente": "G12345678",
        "base_imponible": 3000.00,
        "tipo_iva": 21.00,
        "cuota_iva": 630.00,
        "tipo_retencion": 0.00,
        "retencion": 0.00,
        "total_factura": 3630.00,
        "concepto": "Servicios legales",
        "estado": "pendiente"
    }
    response = requests.post(BASE_URL, json=data)
    print("POST /facturas - Status Code:", response.status_code)
    print("POST /facturas - Response Text:", response.text)  # Agregar esto para ver el texto de la respuesta

# Listar todas las facturas
def test_list_facturas():
    print("=== TEST: Listar Facturas ===")
    response = requests.get(BASE_URL)
    print("GET /facturas - Status Code:", response.status_code)
    print("GET /facturas - Response JSON:", response.json())

# Obtener una factura por ID
def test_get_factura():
    print("=== TEST: Obtener Factura por ID ===")
    
    # Crear una factura y obtener su ID
    data = {
        "fecha": "2024-12-11",
        "numero": "008",  # Usa un número único para evitar conflictos
        "nif_cif_cliente": "G12345678",
        "base_imponible": 3000.00,
        "tipo_iva": 21.00,
        "cuota_iva": 630.00,
        "tipo_retencion": 0.00,
        "retencion": 0.00,
        "total_factura": 3630.00,
        "concepto": "Servicios legales",
        "estado": "pendiente"
    }
    response = requests.post(BASE_URL, json=data)
    factura_creada = response.json()
    factura_id = factura_creada["id"]

    # Obtener la factura recién creada
    response = requests.get(f"{BASE_URL}{factura_id}")
    print(f"GET /facturas/{{id}} - Status Code: {response.status_code}")
    print(f"GET /facturas/{{id}} - Response JSON:", response.json())

if __name__ == "__main__":
    test_create_factura()
    test_list_facturas()
    test_get_factura()
