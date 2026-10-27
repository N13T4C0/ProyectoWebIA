"""Esquemas de entrada y salida de POST /api/recommend."""

from typing import Any

from pydantic import BaseModel, ConfigDict, StrictStr, ValidationError

from app import errors


class RecommendRequest(BaseModel):
    """Obligatorio. Se recortan espacios iniciales y finales; tras recortar, longitud entre 1 y
    `MAX_CARACTERES` (500)."""

    model_config = ConfigDict(extra="ignore")

    tastes: StrictStr


class RecommendResponse(BaseModel):
    resultado: str


class ErrorDetail(BaseModel):
    codigo: str
    mensaje: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


def validate_tastes(payload: Any, max_caracteres: int) -> str:
    """Devuelve `tastes` recortado o lanza `errors.validacion`."""
    if not isinstance(payload, dict):
        raise errors.validacion(max_caracteres)
    try:
        tastes = RecommendRequest.model_validate(payload).tastes.strip()
    except ValidationError:
        raise errors.validacion(max_caracteres) from None
    if not 1 <= len(tastes) <= max_caracteres:
        raise errors.validacion(max_caracteres)
    return tastes
