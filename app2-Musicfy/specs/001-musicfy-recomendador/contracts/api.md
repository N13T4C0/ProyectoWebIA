# Contrato HTTP del backend

Contrato fijo (principio III, INT-01, INT-03). Cualquier cambio exige enmendar antes la ERS y la
constitución.

## POST /api/recommend

**Cabeceras**: `Content-Type: application/json`, `Authorization: Bearer <token de Clerk>`.

**Cuerpo**:

```json
{ "tastes": "Géneros: Indie, Jazz. Además: algo tranquilo para estudiar" }
```

**Orden obligatorio**: verificar token → validar `tastes` → una llamada a la IA.

### Respuestas

| HTTP | Cuándo | Cuerpo |
|---|---|---|
| 200 | Token válido, entrada válida y la IA devuelve texto | `{"resultado": "<texto>"}` |
| 401 | Sin cabecera, esquema no `Bearer`, token mal formado, firma no válida, otro emisor, caducado, `azp` no permitido o JWKS inaccesible. Se aplica aunque el cuerpo también sea inválido. | `{"error": {"codigo": "NO_AUTORIZADO", "mensaje": "Tu sesión no es válida o ha caducado. Inicia sesión de nuevo."}}` |
| 422 | `tastes` ausente, no texto, vacío, solo espacios o > 500 caracteres tras recortar; cuerpo no JSON | `{"error": {"codigo": "VALIDACION", "mensaje": "Describe tus gustos musicales (entre 1 y 500 caracteres)."}}` |
| 502 | Fallo de conexión o respuesta no 2xx del proveedor | `{"error": {"codigo": "IA_NO_DISPONIBLE", "mensaje": "El servicio de recomendaciones no está disponible ahora mismo. Inténtalo más tarde."}}` |
| 502 | Respuesta del proveedor sin texto utilizable | `{"error": {"codigo": "RESPUESTA_INVALIDA", "mensaje": "La IA no ha devuelto recomendaciones válidas. Inténtalo de nuevo."}}` |
| 504 | La IA no responde en `AI_TIMEOUT_SECONDS` | `{"error": {"codigo": "TIMEOUT", "mensaje": "La IA ha tardado demasiado en responder. Inténtalo de nuevo."}}` |
| 500 | Cualquier error inesperado | `{"error": {"codigo": "ERROR_INTERNO", "mensaje": "Se ha producido un error inesperado. Inténtalo más tarde."}}` |

En los 401, 422, 500, 502 y 504 la IA no se consulta (401, 422) o se ha consultado una sola vez
(500 tras la llamada, 502, 504). Ninguna respuesta incluye trazas, claves, tokens ni la respuesta
del proveedor. El número 500 del mensaje de 422 se toma de `MAX_CARACTERES`.

## GET /health

Sin autenticación. `200 {"status": "ok"}`.

## CORS

Orígenes permitidos: `ALLOWED_ORIGINS`. Métodos: `POST`, `GET`, `OPTIONS`. Cabeceras:
`Authorization`, `Content-Type`. Sin credenciales por cookie.

## Llamada saliente a la IA (INT-02)

`POST ${GEMINI_URL}` con `Authorization: Bearer ${GEMINI_API_KEY}` y:

```json
{
  "model": "${GEMINI_MODEL}",
  "messages": [
    {"role": "system", "content": "<instrucciones del recomendador>"},
    {"role": "user", "content": "<tastes recortado>"}
  ],
  "max_tokens": ${MAX_TOKENS}
}
```

Texto utilizado: `choices[0].message.content` recortado y no vacío.
