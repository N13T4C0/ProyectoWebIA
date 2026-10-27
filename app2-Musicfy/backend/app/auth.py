"""Verificación del token de sesión de Clerk con PyJWT + JWKS (research.md R1)."""

from functools import lru_cache

import jwt
from fastapi import Depends, Request

from app import errors
from app.config import Settings, get_settings


class ClerkVerifier:
    def __init__(self, issuer: str, jwks_url: str, allowed_origins: list[str]):
        self.issuer = issuer
        self.allowed_origins = allowed_origins
        self.jwks_client = jwt.PyJWKClient(jwks_url) if issuer and jwks_url else None

    def verify(self, token: str) -> dict:
        try:
            if self.jwks_client is None:
                raise ValueError("emisor de Clerk sin configurar")
            key = self.jwks_client.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=self.issuer,
                leeway=5,
                options={"require": ["exp", "iss"]},
            )
            if "azp" in claims and claims["azp"] not in self.allowed_origins:
                raise ValueError("azp no permitido")
        except Exception:
            raise errors.no_autorizado() from None
        return claims


@lru_cache
def _cached_verifier(issuer: str, jwks_url: str, allowed_origins: tuple[str, ...]) -> ClerkVerifier:
    # Se reutiliza el verificador para que PyJWKClient mantenga las claves en caché.
    return ClerkVerifier(issuer, jwks_url, list(allowed_origins))


def get_verifier(settings: Settings = Depends(get_settings)) -> ClerkVerifier:
    return _cached_verifier(
        settings.CLERK_ISSUER, settings.CLERK_JWKS_URL, tuple(settings.ALLOWED_ORIGINS)
    )


def require_session(request: Request, verifier: ClerkVerifier = Depends(get_verifier)) -> dict:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    token = token.strip()
    if scheme != "Bearer" or not token:
        raise errors.no_autorizado()
    return verifier.verify(token)
