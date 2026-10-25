# Data Model: Musicfy App 2

No hay almacenamiento: todas las entidades viven solo en memoria durante una petición
(principio II). Se describen como modelos de entrada/salida y estados de la pantalla.

## RecommendRequest (DAT-01)

| Campo | Tipo | Reglas |
|---|---|---|
| `tastes` | string | Obligatorio. Se recortan espacios iniciales y finales; tras recortar, longitud entre 1 y `MAX_CARACTERES` (500). Cualquier otro tipo, ausencia, cuerpo no JSON o JSON que no sea un objeto → 422 `VALIDACION`. |

Campos adicionales en el cuerpo: se ignoran.

Composición en el frontend (R6):

| Géneros | Texto libre | `tastes` enviado |
|---|---|---|
| Sí | Sí | `Géneros: A, B. Además: <texto>` |
| Sí | No | `Géneros: A, B.` |
| No | Sí | `<texto>` |
| No | No | No se envía; mensaje «Elige algún género o escribe algo sobre la música que te gusta». |

## RecommendResponse (DAT-02)

| Campo | Tipo | Reglas |
|---|---|---|
| `resultado` | string | Texto de la IA, no vacío tras recortar. |

## ErrorResponse (DAT-03)

| Campo | Tipo | Reglas |
|---|---|---|
| `error.codigo` | string | Uno de `NO_AUTORIZADO`, `VALIDACION`, `TIMEOUT`, `IA_NO_DISPONIBLE`, `RESPUESTA_INVALIDA`, `ERROR_INTERNO`. |
| `error.mensaje` | string | Mensaje en español para el usuario, sin detalles internos (ver `contracts/api.md`). |

## SessionToken (DAT-04)

JWT de Clerk recibido en `Authorization: Bearer <token>`. Claims comprobados: firma (JWKS),
`iss` = `CLERK_ISSUER`, `exp`, `nbf`, `azp` ∈ `ALLOWED_ORIGINS` si existe. Resultado de la
verificación: válido / no válido. No se guarda, no se registra y no se reenvía.

## Configuración (no es dato de usuario)

`Settings` lee las variables de entorno de `research.md` R5 al arrancar. Si falta una variable
obligatoria, la petición afectada responde con el error controlado correspondiente (sin clave
de IA → 502 `IA_NO_DISPONIBLE`; sin `CLERK_ISSUER` → 401), nunca con detalles internos.

## Orden de procesamiento del backend

```text
petición → verificar token ──no──► 401 NO_AUTORIZADO
                 │sí
                 ▼
          validar tastes ──no──► 422 VALIDACION
                 │sí
                 ▼
     una llamada a la IA ──timeout──► 504 TIMEOUT
                 │        ──error/no 2xx──► 502 IA_NO_DISPONIBLE
                 │        ──sin texto──► 502 RESPUESTA_INVALIDA
                 ▼
          200 {resultado}        (excepción inesperada en cualquier punto → 500 ERROR_INTERNO)
```

## Estados de la pantalla (IU-01)

| Estado | Condición | Visible |
|---|---|---|
| `sin-sesion` | `isSignedIn = false` | Título, botón de acceso de Clerk (modal). Formulario no enviable. |
| `entrada` | Sesión, sin petición en curso, sin resultado ni error | Formulario habilitado, botón de cuenta de Clerk. |
| `espera` | Petición en curso | Indicador de carga; botón de envío deshabilitado. |
| `resultado` | Última respuesta 200 | Texto del resultado (sustituye al anterior). |
| `error` | Última respuesta de error o validación local | Mensaje de error; con 401, invita a iniciar sesión de nuevo. |

Transiciones: `sin-sesion → entrada` al iniciar sesión; `entrada|resultado|error → espera` al
enviar con datos; `espera → resultado|error` al responder; cualquier estado `→ sin-sesion` al
cerrar sesión (se borran resultado y error).
