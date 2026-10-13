from fastapi.testclient import TestClient
import main

# El "navegador de mentira" conectado a nuestra app
cliente = TestClient(main.app)


def test_health_responde_ok():
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "ok"