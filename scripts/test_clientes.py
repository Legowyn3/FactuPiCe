import requests
import json
from datetime import datetime
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

def test_clientes(token):
    """Probar endpoints de clientes"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Pruebas de Clientes ===")
    
    # Generar un NIF/CIF único basado en la hora actual
    timestamp = datetime.now().strftime("%H%M%S")
    nif_cif = f"T{timestamp}XX"  # Asegurarnos de que tenga 9 caracteres
    
    # Crear cliente
    cliente_data = {
        "nif_cif": nif_cif,
        "nombre": "Test Company SL",
        "nombre_comercial": "Test Company",  # Opcional
        "direccion": "Calle Test 123",
        "codigo_postal": "28001",  # Debe ser exactamente 5 dígitos
        "ciudad": "Madrid",
        "provincia": "Madrid",
        "pais": "España",  # Opcional, por defecto "España"
        "telefono": "+34666555444",  # Opcional, debe cumplir el patrón
        "email": "test@company.com"  # Opcional
    }
    
    print("\n1. Crear cliente")
    print(f"Enviando datos: {cliente_data}")  # Debug
    response = make_request(requests.post, f"{BASE_URL}/clientes", headers=headers, json=cliente_data)
    print(f"Status: {response.status_code}")
    print(f"Response text: {response.text}")
    wait()
    
    if response.status_code == 200:
        cliente_response = response.json()
        print(f"Response JSON: {cliente_response}")
        cliente_id = cliente_response["id"]
    else:
        raise Exception(f"Error al crear cliente: {response.text}")
    
    # Listar clientes
    print("\n2. Listar clientes")
    response = make_request(requests.get, f"{BASE_URL}/clientes", headers=headers)
    print(f"Status: {response.status_code}")
    wait()
    if response.status_code == 200:
        clientes = response.json()
        print(f"Número de clientes: {len(clientes)}")
        print("Clientes encontrados:")  # Debug
        for cliente in clientes:
            print(f"  - ID: {cliente['id']}, NIF/CIF: {cliente['nif_cif']}, Nombre: {cliente['nombre']}")  # Debug
    else:
        print(f"Error al listar clientes: {response.text}")
    
    # Obtener cliente específico
    print("\n3. Obtener cliente")
    response = make_request(requests.get, f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    wait()
    
    # Actualizar cliente
    print("\n4. Actualizar cliente")
    update_data = {
        "nombre_comercial": "Test Company Updated",
        "telefono": "+34666777888"
    }
    response = make_request(requests.put, f"{BASE_URL}/clientes/{cliente_id}", headers=headers, json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    wait()
    
    # Guardar el ID del cliente para las pruebas de facturas
    with open("cliente_test_id.txt", "w") as f:
        f.write(str(cliente_id))
    print(f"\nID del cliente guardado en cliente_test_id.txt: {cliente_id}")

def main():
    try:
        # Obtener token
        token = login()
        print("✅ Login exitoso")
        
        # Probar endpoints de clientes
        test_clientes(token)
        
        print("\n✅ Todas las pruebas de clientes completadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")

if __name__ == "__main__":
    main()
