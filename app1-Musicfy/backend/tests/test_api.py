from fastapi.testclient import TestClient
import main
from ai_client import AiTimeoutError, AiServiceError, AiInvalidResponseError

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

def test_texto_valido_devuelve_recomendacion(monkeypatch):
    llamadas = []  # aquí apuntamos cada vez que se llama a la IA para comprobar que solo se llama una vez por petición o no se llama si hay error

    # La IA mock: responde siempre lo mismo y apunta que la han llamado
    async def ia_mock(tastes):
        llamadas.append(tastes)
        return {"resultado": "Prueba: escucha a Queen"}

    # Durante este test, main usará la IA mock en vez de la real
    monkeypatch.setattr(main, "ask_model", ia_mock)

    respuesta = cliente.post("/api/recommend", json={"tastes": "rock de los 80"})

    assert respuesta.status_code == 200
    assert respuesta.json()["resultado"] == "Prueba: escucha a Queen"
    assert len(llamadas) == 1                # una sola llamada a la IA
    assert llamadas[0] == "rock de los 80"   # con el texto del usuario


def test_texto_justo_en_el_limite_funciona(monkeypatch):
    async def ia_mock(tastes):
        return {"resultado": "ok"}

    monkeypatch.setattr(main, "ask_model", ia_mock)
    texto = "a" * main.config.MAX_CARACTERES

    respuesta = cliente.post("/api/recommend", json={"tastes": texto})

    assert respuesta.status_code == 200


def test_texto_vacio_no_llama_a_la_ia(monkeypatch):
    llamadas = []

    async def ia_mock(tastes):
        llamadas.append(tastes)
        return {"resultado": "no debería llegar aquí"}

    monkeypatch.setattr(main, "ask_model", ia_mock)

    cliente.post("/api/recommend", json={"tastes": ""})

    assert llamadas == []  # la lista sigue vacía: nadie llamó a la IA


def test_se_quitan_espacios_antes_de_llamar_a_la_ia(monkeypatch):
    llamadas = []

    async def ia_mock(tastes):
        llamadas.append(tastes)
        return {"resultado": "ok"}

    monkeypatch.setattr(main, "ask_model", ia_mock)

    cliente.post("/api/recommend", json={"tastes": "   rock de los 80   "})

    assert llamadas[0] == "rock de los 80"  


def test_ia_tarda_demasiado_da_504(monkeypatch):
    async def ia_lenta_mock(tastes):
        raise AiTimeoutError()

    monkeypatch.setattr(main, "ask_model", ia_lenta_mock)

    respuesta = cliente.post("/api/recommend", json={"tastes": "jazz"})

    assert respuesta.status_code == 504
    assert respuesta.json()["error"]["codigo"] == "TIMEOUT"


def test_ia_falla_da_502(monkeypatch):
    async def ia_rota_mock(tastes):
        raise AiServiceError()

    monkeypatch.setattr(main, "ask_model", ia_rota_mock)

    respuesta = cliente.post("/api/recommend", json={"tastes": "jazz"})

    assert respuesta.status_code == 502
    assert respuesta.json()["error"]["codigo"] == "IA_NO_DISPONIBLE"


def test_ia_responde_algo_roto_da_502(monkeypatch):
    async def ia_rara_mock(tastes):
        raise AiInvalidResponseError()

    monkeypatch.setattr(main, "ask_model", ia_rara_mock)

    respuesta = cliente.post("/api/recommend", json={"tastes": "jazz"})

    assert respuesta.status_code == 502
    assert respuesta.json()["error"]["codigo"] == "RESPUESTA_INVALIDA"