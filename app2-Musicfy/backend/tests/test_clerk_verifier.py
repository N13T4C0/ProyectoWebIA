"""Verificador real de Clerk con claves RSA generadas en la prueba; el JWKS se sustituye (sin red)."""

import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth import ClerkVerifier
from app.errors import ApiError

ISSUER = "https://prueba.clerk.accounts.dev"
ORIGEN = "http://localhost:5173"

CLAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTRA_CLAVE = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def firmar(clave=CLAVE, **claims) -> str:
    ahora = int(time.time())
    payload = {"iss": ISSUER, "sub": "user_prueba", "iat": ahora, "nbf": ahora, "exp": ahora + 60}
    payload.update(claims)
    payload = {k: v for k, v in payload.items() if v is not None}
    return jwt.encode(payload, clave, algorithm="RS256", headers={"kid": "clave-prueba"})


@pytest.fixture
def jwks(monkeypatch):
    """El JWKS siempre devuelve la clave pública de CLAVE."""

    def clave_publica(self, token):
        return SimpleNamespace(key=CLAVE.public_key())

    monkeypatch.setattr(jwt.PyJWKClient, "get_signing_key_from_jwt", clave_publica)


@pytest.fixture
def verifier(jwks):
    return ClerkVerifier(ISSUER, f"{ISSUER}/.well-known/jwks.json", [ORIGEN])


def assert_401(verifier, token):
    with pytest.raises(ApiError) as exc:
        verifier.verify(token)
    assert exc.value.status_code == 401
    assert exc.value.codigo == "NO_AUTORIZADO"


def test_token_valido_pasa(verifier):
    claims = verifier.verify(firmar(azp=ORIGEN))

    assert claims["sub"] == "user_prueba"


def test_token_valido_sin_azp_pasa(verifier):
    assert verifier.verify(firmar())["iss"] == ISSUER


def test_firma_con_otra_clave_da_401(verifier):
    assert_401(verifier, firmar(clave=OTRA_CLAVE, azp=ORIGEN))


def test_otro_emisor_da_401(verifier):
    assert_401(verifier, firmar(iss="https://otra.clerk.accounts.dev", azp=ORIGEN))


def test_token_caducado_da_401(verifier):
    hace_un_rato = int(time.time()) - 120
    assert_401(verifier, firmar(iat=hace_un_rato, nbf=hace_un_rato, exp=hace_un_rato + 60, azp=ORIGEN))


def test_token_aun_no_valido_da_401(verifier):
    futuro = int(time.time()) + 600
    assert_401(verifier, firmar(nbf=futuro, exp=futuro + 60, azp=ORIGEN))


def test_sin_exp_da_401(verifier):
    assert_401(verifier, firmar(exp=None, azp=ORIGEN))


def test_azp_no_permitido_da_401(verifier):
    assert_401(verifier, firmar(azp="https://malicioso.example"))


def test_token_mal_formado_da_401(verifier):
    assert_401(verifier, "esto.no.es-un-jwt")


def test_fallo_del_jwks_da_401(monkeypatch):
    def jwks_caido(self, token):
        raise jwt.PyJWKClientConnectionError("sin conexión")

    monkeypatch.setattr(jwt.PyJWKClient, "get_signing_key_from_jwt", jwks_caido)
    verifier = ClerkVerifier(ISSUER, f"{ISSUER}/.well-known/jwks.json", [ORIGEN])

    assert_401(verifier, firmar(azp=ORIGEN))


def test_sin_emisor_configurado_da_401(jwks):
    assert_401(ClerkVerifier("", "", [ORIGEN]), firmar(azp=ORIGEN))
