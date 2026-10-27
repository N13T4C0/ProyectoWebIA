"""Cliente de la API de Gemini (formato compatible con OpenAI, research.md R3)."""

from typing import Protocol

import httpx
from fastapi import Depends

from app import errors
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
        # Los errores nunca incluyen la respuesta del proveedor.
        settings = self.settings
        if not settings.GEMINI_API_KEY:
            raise errors.ia_no_disponible()
        try:
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
        except httpx.TimeoutException:
            raise errors.timeout() from None
        except httpx.HTTPError:
            raise errors.ia_no_disponible() from None
        if not response.is_success:
            raise errors.ia_no_disponible()
        return _extraer_texto(response)


def _extraer_texto(response: httpx.Response) -> str:
    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (ValueError, LookupError, TypeError):
        raise errors.respuesta_invalida() from None
    if not isinstance(content, str) or not content.strip():
        raise errors.respuesta_invalida()
    return content.strip()


def get_ai_client(settings: Settings = Depends(get_settings)) -> AIClient:
    return GeminiClient(settings)
