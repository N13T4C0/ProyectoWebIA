def test_recomendacion_valida_da_200(client, fake_ai, auth_header):
    """PR-06."""
    response = client.post("/api/recommend", json={"tastes": "Rock y jazz tranquilo"}, headers=auth_header)

    assert response.status_code == 200
    assert response.json() == {"resultado": fake_ai.text}
    assert len(fake_ai.calls) == 1
    assert fake_ai.calls[0] == "Rock y jazz tranquilo"


def test_se_recortan_espacios_antes_de_llamar_a_la_ia(client, fake_ai, auth_header):
    """PR-09."""
    response = client.post("/api/recommend", json={"tastes": "  indie  "}, headers=auth_header)

    assert response.status_code == 200
    assert fake_ai.calls == ["indie"]


def test_campos_extra_se_ignoran(client, fake_ai, auth_header):
    response = client.post(
        "/api/recommend", json={"tastes": "Flamenco", "otro": 1, "user": "x"}, headers=auth_header
    )

    assert response.status_code == 200
    assert fake_ai.calls == ["Flamenco"]
