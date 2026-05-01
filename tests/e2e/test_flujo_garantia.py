import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_registrar_y_listar_equipo():
    response = client.post("/equipos/", json={
        "serial": "TEST-E2E-001",
        "nombre": "Kyocera Test E2E",
        "marca": "Kyocera",
        "modelo": "TASKalfa 2553ci",
        "tipo": "multifuncional_impresion",
        "ubicacion_fisica": "Piso Test",
    })
    # Puede devolver 201 (creado) o 400 (si ya existe de una ejecución anterior)
    assert response.status_code in (201, 400)

    response2 = client.get("/equipos/")
    assert response2.status_code == 200
    assert isinstance(response2.json(), list)


def test_listar_solicitudes():
    response = client.get("/solicitudes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_listar_borradores():
    response = client.get("/borradores/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
