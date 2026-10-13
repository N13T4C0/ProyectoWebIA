from fastapi.testclient import TestClient
import main

# El "navegador de mentira" conectado a nuestra app
cliente = TestClient(main.app)


def test_health_responde_ok():
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "ok"


def test_texto_vacio_da_422():
    respuesta = cliente.post("/api/recommend", json={"tastes": ""})

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_texto_solo_espacios_da_422():
    respuesta = cliente.post("/api/recommend", json={"tastes": "     "})

    assert respuesta.status_code == 422


def test_sin_campo_tastes_da_422():
    respuesta = cliente.post("/api/recommend", json={})

    assert respuesta.status_code == 422


def test_texto_demasiado_largo_da_422():
    # Uno más que el máximo permitido
    texto = "a" * (main.config.MAX_CARACTERES + 1)

    respuesta = cliente.post("/api/recommend", json={"tastes": texto})

    assert respuesta.status_code == 422