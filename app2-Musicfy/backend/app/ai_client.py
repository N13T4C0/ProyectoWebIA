"""Cliente de la API de Gemini (formato compatible con OpenAI, research.md R3)."""

from typing import Protocol

import httpx
from fastapi import Depends

from app.config import Settings, get_settings

# Instrucciones fijas del recomendador (research.md R4).
SYSTEM_PROMPT = (
    "Eres un recomendador musical. A partir de los gustos que describe el usuario, recomienda "
    "entre 3 y 5 artistas y explica brevemente por qué encaja cada uno. Responde siempre en "
    "español y en texto plano, sin HTML ni Markdown."
)


class AIClient(Protocol):
    async def recommend(self, tastes: str) -> str: ...


class GeminiClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.transport = transport

    async def recommend(self, tastes: str) -> str:
        # Solo se envía el texto validado: ningún dato de identidad del usuario.
        # La traducción de fallos a errores del contrato llega en US4 (T031).
        settings = self.settings
        async with httpx.AsyncClient(
            timeout=settings.AI_TIMEOUT_SECONDS, transport=self.transport
        ) as client:
            response = await client.post(
                settings.GEMINI_URL,
                headers={"Authorization": f"Bearer {settings.GEMINI_API_KEY}"},
                json={
                    "model": settings.GEMINI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": tastes},
                    ],
                    "max_tokens": settings.MAX_TOKENS,
                },
            )
        return response.json()["choices"][0]["message"]["content"].strip()


def get_ai_client(settings: Settings = Depends(get_settings)) -> AIClient:
    return GeminiClient(settings)
