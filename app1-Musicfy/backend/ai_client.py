import httpx

try:
    from . import config
except ImportError:
    import config

SYSTEM_PROMPT = (
    "Eres el recomendador musical inteligente de Musicfy. A partir de los gustos, "
    "artistas, géneros, épocas o sensaciones que te describa el usuario, recomienda "
    "entre 3 y 5 artistas o bandas afines que puedan gustarle.\n\n"
    "Reglas:\n"
    "- No recomiendes artistas que el usuario ya haya nombrado.\n"
    "- Mezcla artistas conocidos con alguno menos conocido para que descubra música nueva.\n"
    "- Cita solo canciones y álbumes que existan de verdad.\n"
    "- Explica la relación con lo que ha pedido el usuario.\n\n"
    "Formato obligatorio, sin excepciones:\n"
    "- Cada recomendación empieza en una línea nueva con su número, un punto, el nombre "
    "del artista, un guion largo (–) y una o dos frases de por qué encaja.\n"
    "- En la línea siguiente, con tres espacios delante, escribe Escucha: y una canción "
    "o álbum para empezar.\n"
    "- Deja una línea en blanco entre recomendaciones.\n"
    "- Sin introducción ni despedida, sin títulos y sin markdown (nada de **, * ni #).\n\n"
    "Ejemplo de formato (el contenido es solo ilustrativo):\n"
    "1. Tycho – Paisajes electrónicos cálidos con guitarras y sintetizadores, "
    "perfecto si buscas algo tranquilo pero melódico.\n"
    "   Escucha: \"Awake\" (álbum Awake)\n\n"
    "2. Khruangbin – Groove relajado con influencias del funk tailandés, ideal para "
    "el lado más orgánico de lo que te gusta.\n"
    "   Escucha: \"Maria También\" (álbum Con Todo El Mundo)\n\n"
    "Responde siempre en español."
)


class AiError(Exception):
    """Excepción base para fallos relacionados con la IA."""
    def __init__(self, codigo: str, mensaje: str, status_code: int = 502):
        self.codigo = codigo
        self.mensaje = mensaje
        self.status_code = status_code
        super().__init__(mensaje)


class AiTimeoutError(AiError):
    """Error cuando la IA tarda más del tiempo establecido."""
    def __init__(self, mensaje: str = "La IA ha tardado demasiado en responder."):
        super().__init__(codigo="TIMEOUT", mensaje=mensaje, status_code=504)


class AiServiceError(AiError):
    """Error cuando el servicio de IA falla o devuelve un código HTTP no exitoso."""
    def __init__(self, mensaje: str = "No se ha podido completar la consulta con el servicio de IA."):
        super().__init__(codigo="IA_NO_DISPONIBLE", mensaje=mensaje, status_code=502)


class AiInvalidResponseError(AiError):
    """Error cuando la respuesta devuelta por la IA no tiene el formato esperado."""
    def __init__(self, mensaje: str = "La respuesta de la IA no tiene el formato esperado."):
        super().__init__(codigo="RESPUESTA_INVALIDA", mensaje=mensaje, status_code=502)


async def ask_model(tastes: str) -> dict:
    """Envía los gustos musicales a OpenRouter y devuelve el resultado estructurado."""
    if not config.OPENROUTER_API_KEY:
        raise AiServiceError("No se ha configurado la clave de API de OpenRouter.")

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://musicfy.local",
        "X-Title": "Musicfy",
    }

    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": tastes},
        ],
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=config.AI_TIMEOUT_SECONDS) as client:
            response = await client.post(
                config.OPENROUTER_URL,
                headers=headers,
                json=payload,
            )
    except httpx.TimeoutException:
        raise AiTimeoutError()
    except httpx.RequestError:
        raise AiServiceError("No se ha podido conectar con el servicio de IA.")

    if response.status_code != 200:
        raise AiServiceError("El servicio de IA ha respondido con un error.")

    try:
        data = response.json()
        choices = data.get("choices")
        if not choices or not isinstance(choices, list):
            raise AiInvalidResponseError()

        content = choices[0].get("message", {}).get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise AiInvalidResponseError()

        return {"resultado": content.strip()}
    except (ValueError, KeyError, TypeError):
        raise AiInvalidResponseError()
