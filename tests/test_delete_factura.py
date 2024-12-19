import requests

BASE_URL = "http://127.0.0.1:8000/facturas/"

def test_delete_factura():
    # ID de la factura a eliminar
    factura_id = 3

    # Solicitud DELETE
    response = requests.delete(f"{BASE_URL}{factura_id}")

    print("DELETE /facturas/{id} - Status Code:", response.status_code)
    print("DELETE /facturas/{id} - Response JSON:", response.json())

if __name__ == "__main__":
    test_delete_factura()
