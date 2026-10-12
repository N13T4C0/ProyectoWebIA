from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

try:
    from . import config
    from .ai_client import ask_model, AiError
except ImportError:
    import config
    from ai_client import ask_model, AiError

app = FastAPI(title="Musicfy API - Recomendador Musical")

# Configuración de CORS para permitir la conexión desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    tastes: str

    @field_validator("tastes")
    @classmethod
    def validate_tastes(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("El campo 'tastes' debe ser una cadena de texto.")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("El texto no puede estar vacío.")
        if len(trimmed) > config.MAX_CARACTERES:
            raise ValueError(f"El texto supera el límite de {config.MAX_CARACTERES} caracteres.")
        return trimmed


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejo personalizado de errores de validación de entrada (422)."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "codigo": "VALIDACION",
                "mensaje": f"El texto no puede estar vacío ni superar los {config.MAX_CARACTERES} caracteres.",
            }
        },
    )


@app.exception_handler(AiError)
async def ai_error_handler(request: Request, exc: AiError):
    """Manejo controlado de excepciones del servicio de IA (502 / 504)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "codigo": exc.codigo,
                "mensaje": exc.mensaje,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Captura cualquier error inesperado para evitar fugas de información interna."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "codigo": "ERROR_INTERNO",
                "mensaje": "Ha ocurrido un error inesperado en el servidor.",
            }
        },
    )


@app.get("/health")
async def health():
    """Endpoint de comprobación de estado."""
    return {"status": "ok", "app": "Musicfy Backend"}


@app.post("/api/recommend")
async def recommend(body: RecommendRequest):
    """Endpoint principal de recomendación musical."""
    return await ask_model(body.tastes)