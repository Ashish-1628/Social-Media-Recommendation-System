import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    # Register
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "secret123"},
    )
    assert reg.status_code == 201
    assert reg.json()["username"] == "testuser"

    # Duplicate registration should fail
    dup = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser2", "email": "test@example.com", "password": "secret123"},
    )
    assert dup.status_code == 400

    # Login
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_wrong_password():
    client.post(
        "/api/v1/auth/register",
        json={"username": "pwtest", "email": "pwtest@example.com", "password": "correct"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "pwtest@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
