"""Dobles de la IA y del verificador de Clerk. Ninguna prueba usa .env ni red."""

import pytest
from fastapi.testclient import TestClient

from app import errors
from app.ai_client import get_ai_client
from app.auth import get_verifier
from app.main import app


class FakeVerifier:
    """Acepta solo el token "valido"; registra los tokens recibidos."""

    def __init__(self):
        self.calls = []

    def verify(self, token: str) -> dict:
        self.calls.append(token)
        if token != "valido":
            raise errors.no_autorizado()
        return {"sub": "user_prueba"}


class FakeAIClient:
    """Devuelve `text` o lanza `exc`; registra cada `tastes` recibido."""

    def __init__(self, text: str = "Recomendaciones simuladas", exc: Exception | None = None):
        self.text = text
        self.exc = exc
        self.calls = []

    async def recommend(self, tastes: str) -> str:
        self.calls.append(tastes)
        if self.exc is not None:
            raise self.exc
        return self.text


@pytest.fixture
def fake_ai():
    return FakeAIClient()


@pytest.fixture
def fake_verifier():
    return FakeVerifier()


@pytest.fixture
def client(fake_ai, fake_verifier):
    app.dependency_overrides[get_verifier] = lambda: fake_verifier
    app.dependency_overrides[get_ai_client] = lambda: fake_ai
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer valido"}
