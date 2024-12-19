import requests
import json
from datetime import date
import time

BASE_URL = "http://localhost:8000/api"

def wait():
    """Esperar un breve momento entre requests"""
    time.sleep(2.0)  # 2 segundos de espera

def make_request(method, url, headers=None, json=None, max_retries=3):
    """Hacer una petición HTTP con reintentos en caso de rate limiting"""
    for attempt in range(max_retries):
        response = method(url, headers=headers, json=json)
        if response.status_code != 429:  # Si no es rate limit, retornar inmediatamente
            return response
        
        # Si es rate limit, esperar más tiempo antes de reintentar
        wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
        print(f"Rate limit alcanzado, esperando {wait_time} segundos antes de reintentar...")
        time.sleep(wait_time)
    
    # Si llegamos aquí, retornar la última respuesta (probablemente un error)
    return response

def login():
    """Obtener token de autenticación"""
    response = make_request(
        requests.post,
        f"{BASE_URL}/token",
        json={
            "username": "admin@example.com",
            "password": "Admin123!@#$",
            "mfa_token": None
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Error de login: {response.text}")

def test_facturas(token):
    """Probar endpoints de facturas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Pruebas de Facturas ===")
    
    # Leer el ID del cliente de prueba
    try:
        with open("cliente_test_id.txt", "r") as f:
            cliente_id = int(f.read().strip())
        print(f"ID del cliente cargado: {cliente_id}")
    except FileNotFoundError:
        raise Exception("Por favor, ejecuta primero test_clientes.py para crear un cliente de prueba")
    
    # Crear factura usando el cliente_id proporcionado
    factura_data = {
        "fecha": str(date.today()),
        "numero": "2024/TEST/001",
        "cliente_id": cliente_id,
        "base_imponible": 1000.0,
        "tipo_iva": 21.0,
        "concepto": "Servicios de prueba",
        "estado": "borrador"
    }
    
    print("\n1. Crear factura")
    print(f"Enviando datos: {factura_data}")  # Debug
    response = make_request(requests.post, f"{BASE_URL}/facturas", headers=headers, json=factura_data)
    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}")
    wait()
    
    if response.status_code == 200:
        factura_response = response.json()
        print(f"Response JSON: {factura_response}")
        factura_id = factura_response["id"]
    else:
        raise Exception(f"Error al crear factura: {response.text}")
    
    # Listar facturas
    print("\n2. Listar facturas")
    response = make_request(requests.get, f"{BASE_URL}/facturas", headers=headers)
    print(f"Status: {response.status_code}")
    wait()
    if response.status_code == 200:
        facturas = response.json()
        print(f"Número de facturas: {len(facturas)}")
        print("Facturas encontradas:")  # Debug
        for factura in facturas:
            print(f"  - ID: {factura['id']}, Número: {factura['numero']}, Cliente: {factura['cliente']['nombre'] if factura['cliente'] else 'N/A'}")
    else:
        print(f"Error al listar facturas: {response.text}")
    
    # Obtener factura específica
    print("\n3. Obtener factura")
    response = make_request(requests.get, f"{BASE_URL}/facturas/{factura_id}", headers=headers)
    print(f"Status: {response.status_code}")
    wait()
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error al obtener factura: {response.text}")
    
    # Actualizar factura
    print("\n4. Actualizar factura")
    update_data = {
        "estado": "emitida",
        "notas": "Factura de prueba actualizada"
    }
    response = make_request(requests.put, f"{BASE_URL}/facturas/{factura_id}", headers=headers, json=update_data)
    print(f"Status: {response.status_code}")
    wait()
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error al actualizar factura: {response.text}")

def main():
    try:
        # Obtener token
        token = login()
        print("✅ Login exitoso")
        
        # Probar endpoints de facturas
        test_facturas(token)
        
        print("\n✅ Todas las pruebas de facturas completadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")

if __name__ == "__main__":
    main()
