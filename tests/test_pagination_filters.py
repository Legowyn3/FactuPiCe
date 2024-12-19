import requests

BASE_URL = "http://127.0.0.1:8000/facturas"

def test_pagination():
    print("\n=== TEST: Paginación ===")
    params = {"skip": 0, "limit": 2}
    response = requests.get(BASE_URL, params=params)
    print("GET /facturas with pagination - Status Code:", response.status_code)
    print("GET /facturas with pagination - Response JSON:", response.json())

def test_filter_by_date():
    print("\n=== TEST: Filtrar por Fecha ===")
    params = {"fecha": "2024-12-11"}
    response = requests.get(BASE_URL, params=params)
    print("GET /facturas with filter by date - Status Code:", response.status_code)
    print("GET /facturas with filter by date - Response JSON:", response.json())

def test_filter_by_estado():
    print("\n=== TEST: Filtrar por Estado ===")
    params = {"estado": "pendiente"}
    response = requests.get(BASE_URL, params=params)
    print("GET /facturas with filter by estado - Status Code:", response.status_code)
    print("GET /facturas with filter by estado - Response JSON:", response.json())

if __name__ == "__main__":
    test_pagination()
    test_filter_by_date()
    test_filter_by_estado()
