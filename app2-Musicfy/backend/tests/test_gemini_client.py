"""GeminiClient con httpx.MockTransport: ninguna petición sale a la red."""

import asyncio
import json
from dataclasses import replace

import httpx
import pytest

from app.ai_client import SYSTEM_PROMPT, GeminiClient
from app.config import Settings
from app.errors import ApiError

SETTINGS = Settings(
    GEMINI_API_KEY="clave-de-prueba",
    GEMINI_URL="https://gemini.prueba/v1beta/openai/chat/completions",
    GEMINI_MODEL="modelo-prueba",
    MAX_TOKENS=600,
    AI_TIMEOUT_SECONDS=25,
    MAX_CARACTERES=500,
    CLERK_ISSUER="",
    CLERK_JWKS_URL="",
    ALLOWED_ORIGINS=[],
)


def respuesta_con(content) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def recomendar(handler, settings=SETTINGS, tastes="indie"):
    client = GeminiClient(settings, transport=httpx.MockTransport(handler))
    return asyncio.run(client.recommend(tastes))


def assert_error(handler, codigo, settings=SETTINGS):
    with pytest.raises(ApiError) as exc:
        recomendar(handler, settings)
    assert exc.value.codigo == codigo


def test_respuesta_valida_devuelve_el_texto_recortado():
    peticiones = []

    def handler(request):
        peticiones.append(request)
        return httpx.Response(200, json=respuesta_con("  Texto  "))

    assert recomendar(handler) == "Texto"

    [request] = peticiones
    assert str(request.url) == SETTINGS.GEMINI_URL
    assert request.headers["Authorization"] == "Bearer clave-de-prueba"
    assert json.loads(request.content) == {
        "model": "modelo-prueba",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "indie"},
        ],
        "max_tokens": 600,
    }


def test_timeout_da_TIMEOUT():
    def handler(request):
        raise httpx.ReadTimeout("tiempo agotado", request=request)

    assert_error(handler, "TIMEOUT")


def test_fallo_de_conexion_da_IA_NO_DISPONIBLE():
    def handler(request):
        raise httpx.ConnectError("sin conexión", request=request)

    assert_error(handler, "IA_NO_DISPONIBLE")


@pytest.mark.parametrize("status", [400, 401, 429, 500, 503])
def test_estado_no_2xx_da_IA_NO_DISPONIBLE(status):
    def handler(request):
        return httpx.Response(status, json={"error": {"message": "detalle-del-proveedor"}})

    with pytest.raises(ApiError) as exc:
        recomendar(handler)
    assert exc.value.codigo == "IA_NO_DISPONIBLE"
    assert "detalle-del-proveedor" not in exc.value.mensaje


@pytest.mark.parametrize(
    "respuesta",
    [
        httpx.Response(200, json=respuesta_con("")),
        httpx.Response(200, json=respuesta_con("   ")),
        httpx.Response(200, json=respuesta_con(None)),
        httpx.Response(200, json=respuesta_con(42)),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, json={}),
        httpx.Response(200, json=["no", "es", "un", "objeto"]),
        httpx.Response(200, content=b"<html>no es json</html>"),
    ],
    ids=["vacio", "espacios", "null", "numero", "choices-vacio", "sin-choices", "lista", "no-json"],
)
def test_respuesta_sin_texto_util_da_RESPUESTA_INVALIDA(respuesta):
    assert_error(lambda request: respuesta, "RESPUESTA_INVALIDA")


def test_sin_clave_da_IA_NO_DISPONIBLE_sin_hacer_la_peticion():
    peticiones = []

    def handler(request):
        peticiones.append(request)
        return httpx.Response(200, json=respuesta_con("Texto"))

    assert_error(handler, "IA_NO_DISPONIBLE", settings=replace(SETTINGS, GEMINI_API_KEY=""))
    assert peticiones == []
