"""Configuración leída de variables de entorno (research.md R5).

Las variables obligatorias que falten quedan vacías: la app arranca y el fallo
aparece al usarlas (401 sin emisor de Clerk, 502 sin clave de Gemini).
"""

import os
from dataclasses import dataclass
from functools import lru_cache

DEFAULT_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


def _int(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _origins(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    GEMINI_API_KEY: str
    GEMINI_URL: str
    GEMINI_MODEL: str
    MAX_TOKENS: int
    AI_TIMEOUT_SECONDS: int
    MAX_CARACTERES: int
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str
    ALLOWED_ORIGINS: list[str]

    @classmethod
    def from_env(cls) -> "Settings":
        issuer = os.environ.get("CLERK_ISSUER", "").strip().rstrip("/")
        jwks_url = os.environ.get("CLERK_JWKS_URL", "").strip()
        if not jwks_url and issuer:
            jwks_url = f"{issuer}/.well-known/jwks.json"
        return cls(
            GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY", "").strip(),
            GEMINI_URL=os.environ.get("GEMINI_URL", "").strip() or DEFAULT_GEMINI_URL,
            GEMINI_MODEL=os.environ.get("GEMINI_MODEL", "").strip() or "gemini-3.5-flash-lite",
            MAX_TOKENS=_int("MAX_TOKENS", 600),
            AI_TIMEOUT_SECONDS=_int("AI_TIMEOUT_SECONDS", 25),
            MAX_CARACTERES=_int("MAX_CARACTERES", 500),
            CLERK_ISSUER=issuer,
            CLERK_JWKS_URL=jwks_url,
            ALLOWED_ORIGINS=_origins(os.environ.get("ALLOWED_ORIGINS", "")),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
