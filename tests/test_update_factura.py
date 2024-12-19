import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from .fixtures import create_test_user, create_test_factura

@pytest.fixture
def factura_update_data():
    return {
        "fecha": "2024-12-12",
        "numero": "010",
        "nif_cif_cliente": "G98765432",
        "base_imponible": 1500.0,
        "tipo_iva": 10.0,
        "cuota_iva": 150.0,
        "tipo_retencion": 2.0,
        "retencion": 30.0,
        "total_factura": 1620.0,
        "concepto": "Servicios de consultoría",
        "estado": "pagada"
    }

@pytest.fixture
def test_user(db):
    return create_test_user(db)

@pytest.fixture
def test_factura(db, test_user):
    return create_test_factura(db, test_user.id)

@pytest.fixture
def auth_headers(client, test_user):
    login_data = {"username": "test@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_update_factura_success(client, auth_headers, factura_update_data, test_factura):
    response = client.put(f"/facturas/{test_factura.id}", json=factura_update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["numero"] == factura_update_data["numero"]
    assert data["total_factura"] == factura_update_data["total_factura"]

def test_update_factura_not_found(client, auth_headers, factura_update_data):
    response = client.put("/facturas/999", json=factura_update_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

def test_update_factura_invalid_data(client, auth_headers, test_factura):
    invalid_data = {"total_factura": "invalid"}
    response = client.put(f"/facturas/{test_factura.id}", json=invalid_data, headers=auth_headers)
    assert response.status_code == 422

def test_update_factura_unauthorized(client, test_factura):
    response = client.put(f"/facturas/{test_factura.id}", json={})
    assert response.status_code == 401

def test_update_factura_with_special_characters(client, auth_headers, test_factura):
    special_data = {"concepto": "Servicios & consultoría (ñ) áéíóú"}
    response = client.put(f"/facturas/{test_factura.id}", json=special_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["concepto"] == special_data["concepto"]

def test_update_factura_estado_transition(client, auth_headers, test_factura):
    # Cambiar a estado pendiente
    response1 = client.put(
        f"/facturas/{test_factura.id}", 
        json={"estado": "pendiente"}, 
        headers=auth_headers
    )
    assert response1.status_code == 200

    # Cambiar a estado pagada
    response2 = client.put(
        f"/facturas/{test_factura.id}", 
        json={"estado": "pagada"}, 
        headers=auth_headers
    )
    assert response2.status_code == 200

def test_update_factura_validation_limits(client, auth_headers, test_factura):
    invalid_cases = [
        {"base_imponible": -100.0},
        {"tipo_iva": 101.0},
        {"concepto": "a" * 1001},
        {"numero": ""}
    ]
    
    for invalid_field in invalid_cases:
        response = client.put(
            f"/facturas/{test_factura.id}", 
            json=invalid_field, 
            headers=auth_headers
        )
        assert response.status_code == 422