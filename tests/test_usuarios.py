import pytest
from fastapi.testclient import TestClient

def test_crear_usuario(client):
    """Test crear un nuevo usuario"""
    response = client.post(
        "/api/usuarios",
        json={
            "email": "test@example.com",
            "password": "test123",
            "nombre": "Test User",
            "es_admin": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nombre"] == "Test User"
    assert "id" in data

def test_crear_usuario_duplicado(client):
    """Test intentar crear un usuario con email duplicado"""
    # Crear primer usuario
    response1 = client.post(
        "/api/usuarios",
        json={
            "email": "duplicate@example.com",
            "password": "test123",
            "nombre": "First User",
            "es_admin": False
        }
    )
    assert response1.status_code == 200

    # Intentar crear usuario duplicado
    response2 = client.post(
        "/api/usuarios",
        json={
            "email": "duplicate@example.com",
            "password": "test123",
            "nombre": "Second User",
            "es_admin": False
        }
    )
    assert response2.status_code == 400
    assert "Email ya registrado" in response2.json()["detail"]

def test_login_correcto(client):
    """Test login con credenciales correctas"""
    # Crear usuario
    client.post(
        "/api/usuarios",
        json={
            "email": "login@example.com",
            "password": "test123",
            "nombre": "Login Test",
            "es_admin": False
        }
    )

    # Intentar login
    response = client.post(
        "/api/token",
        data={
            "username": "login@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_incorrecto(client):
    """Test login con credenciales incorrectas"""
    response = client.post(
        "/api/token",
        data={
            "username": "wrong@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"]
