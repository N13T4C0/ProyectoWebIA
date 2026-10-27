def test_health_sin_token_da_200(client):
    """PR-01."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
