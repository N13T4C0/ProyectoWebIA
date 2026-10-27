import pytest

from app.config import get_settings


def validacion(max_caracteres: int = 500) -> dict:
    return {
        "error": {
            "codigo": "VALIDACION",
            "mensaje": f"Describe tus gustos musicales (entre 1 y {max_caracteres} caracteres).",
        }
    }


def test_texto_vacio_da_422_sin_llamar_a_la_ia(client, fake_ai, auth_header):
    """PR-02 y PR-08."""
    response = client.post("/api/recommend", json={"tastes": ""}, headers=auth_header)

    assert response.status_code == 422
    assert response.json() == validacion()
    assert fake_ai.calls == []


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"tastes": "   "},  # PR-03
        {},  # PR-04
        {"tastes": "a" * 501},  # PR-05
        {"tastes": 123},
        {"tastes": None},
        {"tastes": ["rock"]},
        ["rock"],
        "rock",
    ],
    ids=["solo-espacios", "sin-tastes", "501", "numero", "null", "lista", "cuerpo-lista", "cuerpo-texto"],
)
def test_entrada_no_valida_da_422(client, fake_ai, auth_header, cuerpo):
    response = client.post("/api/recommend", json=cuerpo, headers=auth_header)

    assert response.status_code == 422
    assert response.json() == validacion()
    assert fake_ai.calls == []


def test_cuerpo_no_json_da_422(client, fake_ai, auth_header):
    response = client.post(
        "/api/recommend",
        content=b"esto no es json",
        headers={**auth_header, "Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json() == validacion()
    assert fake_ai.calls == []


def test_500_caracteres_da_200(client, fake_ai, auth_header):
    """PR-07."""
    response = client.post("/api/recommend", json={"tastes": "a" * 500}, headers=auth_header)

    assert response.status_code == 200
    assert fake_ai.calls == ["a" * 500]


def test_longitud_se_cuenta_tras_recortar(client, fake_ai, auth_header):
    response = client.post("/api/recommend", json={"tastes": "  " + "a" * 500 + "  "}, headers=auth_header)

    assert response.status_code == 200
    assert fake_ai.calls == ["a" * 500]


@pytest.fixture
def max_caracteres_10(monkeypatch):
    monkeypatch.setenv("MAX_CARACTERES", "10")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_limite_configurable_se_refleja_en_el_mensaje(client, fake_ai, auth_header, max_caracteres_10):
    response = client.post("/api/recommend", json={"tastes": "a" * 11}, headers=auth_header)

    assert response.status_code == 422
    assert response.json() == validacion(10)
    assert fake_ai.calls == []
