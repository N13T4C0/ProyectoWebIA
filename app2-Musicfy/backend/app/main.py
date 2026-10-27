"""Aplicación FastAPI de Musicfy App 2."""

import logging

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import errors
from app.ai_client import get_ai_client
from app.auth import require_session
from app.config import get_settings
from app.schemas import validate_tastes

# Solo se registra el código de error: nunca tastes, resultado, tokens ni claves.
logger = logging.getLogger("musicfy")

settings = get_settings()

app = FastAPI(title="Musicfy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)


def _error_response(err: errors.ApiError) -> JSONResponse:
    return JSONResponse(status_code=err.status_code, content=errors.error_body(err))


@app.exception_handler(errors.ApiError)
async def api_error_handler(request: Request, exc: errors.ApiError) -> JSONResponse:
    logger.info("error %s", exc.codigo)
    return _error_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.info("error VALIDACION")
    return _error_response(errors.validacion(get_settings().MAX_CARACTERES))


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("error ERROR_INTERNO (%s)", type(exc).__name__)
    return _error_response(errors.error_interno())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/recommend")
async def recommend(request: Request, _=Depends(require_session), ai=Depends(get_ai_client)) -> dict:
    # El cuerpo no es un parámetro: así la sesión se verifica antes de validar (research.md R2).
    max_caracteres = get_settings().MAX_CARACTERES
    try:
        payload = await request.json()
    except ValueError:
        raise errors.validacion(max_caracteres) from None
    tastes = validate_tastes(payload, max_caracteres)
    resultado = await ai.recommend(tastes)
    return {"resultado": resultado}
