"""Errores del contrato (contracts/api.md). Los mensajes se copian literalmente."""


class ApiError(Exception):
    def __init__(self, status_code: int, codigo: str, mensaje: str):
        super().__init__(codigo)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje


def no_autorizado() -> ApiError:
    return ApiError(401, "NO_AUTORIZADO", "Tu sesión no es válida o ha caducado. Inicia sesión de nuevo.")


def validacion(max_caracteres: int) -> ApiError:
    return ApiError(
        422, "VALIDACION", f"Describe tus gustos musicales (entre 1 y {max_caracteres} caracteres)."
    )


def timeout() -> ApiError:
    return ApiError(504, "TIMEOUT", "La IA ha tardado demasiado en responder. Inténtalo de nuevo.")


def ia_no_disponible() -> ApiError:
    return ApiError(
        502,
        "IA_NO_DISPONIBLE",
        "El servicio de recomendaciones no está disponible ahora mismo. Inténtalo más tarde.",
    )


def respuesta_invalida() -> ApiError:
    return ApiError(
        502, "RESPUESTA_INVALIDA", "La IA no ha devuelto recomendaciones válidas. Inténtalo de nuevo."
    )


def error_interno() -> ApiError:
    return ApiError(500, "ERROR_INTERNO", "Se ha producido un error inesperado. Inténtalo más tarde.")


def error_body(err: ApiError) -> dict:
    return {"error": {"codigo": err.codigo, "mensaje": err.mensaje}}
