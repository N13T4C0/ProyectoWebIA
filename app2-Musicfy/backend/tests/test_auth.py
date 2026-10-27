import pytest

NO_AUTORIZADO = {
    "error": {
        "codigo": "NO_AUTORIZADO",
        "mensaje": "Tu sesión no es válida o ha caducado. Inicia sesión de nuevo.",
    }
}


def test_sin_token_da_401(client, fake_ai):
    """PR-18."""
    response = client.post("/api/recommend", json={"tastes": "Rock"})

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_ai.calls == []


def test_token_invalido_da_401(client, fake_ai):
    """PR-19."""
    response = client.post(
        "/api/recommend", json={"tastes": "Rock"}, headers={"Authorization": "Bearer otro"}
    )

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_ai.calls == []


def test_token_caducado_da_401(client, fake_ai, fake_verifier):
    """PR-20. El doble rechaza el token igual que el verificador real con un `exp` pasado."""
    response = client.post(
        "/api/recommend", json={"tastes": "Rock"}, headers={"Authorization": "Bearer caducado"}
    )

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_verifier.calls == ["caducado"]
    assert fake_ai.calls == []


@pytest.mark.parametrize("cabecera", ["Basic valido", "bearer valido", "Bearer ", "Bearer", "valido"])
def test_cabecera_mal_formada_da_401(client, fake_ai, cabecera):
    response = client.post("/api/recommend", json={"tastes": "Rock"}, headers={"Authorization": cabecera})

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_ai.calls == []


def test_sin_token_y_cuerpo_vacio_da_401_no_422(client, fake_ai):
    response = client.post("/api/recommend", json={})

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_ai.calls == []


def test_sin_token_y_cuerpo_no_json_da_401_no_422(client, fake_ai):
    response = client.post(
        "/api/recommend", content=b"esto no es json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 401
    assert response.json() == NO_AUTORIZADO
    assert fake_ai.calls == []
