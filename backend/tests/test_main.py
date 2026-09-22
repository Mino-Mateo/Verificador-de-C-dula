from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_listar_paises():
    response = client.get("/api/paises")
    assert response.status_code == 200
    paises = response.json()
    assert set(paises) == {"EC", "CL", "MX"}


def test_validar_cedula_ecuatoriana_valida():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "1712345675"})
    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is True
    assert body["mensaje"] == "Cédula válida"


def test_validar_cedula_ecuatoriana_invalida():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "1712345670"})
    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is False


def test_pais_no_soportado():
    response = client.post("/api/validate", json={"pais": "CO", "valor": "123456"})
    assert response.status_code == 400
    assert response.json() == {"error": "País no soportado"}


def test_valor_vacio():
    response = client.post("/api/validate", json={"pais": "EC", "valor": "   "})
    assert response.status_code == 400
    assert response.json() == {"error": "Valor vacío"}


def test_pais_case_insensitive():
    response = client.post("/api/validate", json={"pais": "ec", "valor": "1712345675"})
    assert response.status_code == 200
    assert response.json()["valido"] is True
