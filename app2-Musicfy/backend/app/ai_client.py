"""Cliente de la API de Gemini (formato compatible con OpenAI, research.md R3)."""

from typing import Protocol

import httpx
from fastapi import Depends

from app.config import Settings, get_settings


class AIClient(Protocol):
    async def recommend(self, tastes: str) -> str: ...


class GeminiClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.transport = transport

    async def recommend(self, tastes: str) -> str:
        # Se implementa en US1 (T017) y US4 (T031).
        raise NotImplementedError


def get_ai_client(settings: Settings = Depends(get_settings)) -> AIClient:
    return GeminiClient(settings)
