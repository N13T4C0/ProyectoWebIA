# Research: Musicfy App 2

Fase 0 del plan. Cada decisión resuelve una incógnita del contexto técnico o una elección de
tecnología indicada por el equipo. No queda ningún `NEEDS CLARIFICATION`.

## R1. Verificación del token de Clerk

- **Decision**: PyJWT (`pyjwt[crypto]`) con `PyJWKClient` sobre el JWKS público del emisor de
  Clerk. Se verifica: firma RS256 con la clave del `kid` del token, `iss` igual a
  `CLERK_ISSUER`, `exp` y `nbf` (con un margen de 5 s), y `azp` incluido en `ALLOWED_ORIGINS`
  cuando el claim está presente. Cualquier fallo (cabecera ausente, esquema distinto de
  `Bearer`, token mal formado, firma, emisor, caducidad, `azp` o JWKS inaccesible) produce
  `401 NO_AUTORIZADO`.
- **Rationale**: no necesita la clave secreta de Clerk en el backend (solo URLs públicas), con lo
  que el principio I se cumple con menos secretos; es la verificación manual documentada por
  Clerk (FUE-07); la lógica se puede probar sin red generando un par RSA en la prueba.
  `PyJWKClient` cachea las claves, así que no se consulta el JWKS en cada petición.
- **Alternatives considered**: SDK oficial `clerk-backend-api` (`authenticate_request`):
  válido, pero exige `CLERK_SECRET_KEY` en el backend y añade una dependencia más pesada; queda
  como alternativa si el equipo la prefiere, sin cambiar el contrato. Decodificar sin verificar:
  prohibido por RF-06.

## R2. Orden verificar → validar → IA (principio IV)

- **Decision**: el endpoint no declara el cuerpo como parámetro Pydantic. Su firma solo recibe
  `Request` y la dependencia `require_session`; dentro del endpoint se lee el JSON y se valida
  con el modelo Pydantic `RecommendRequest`.
- **Rationale**: si el cuerpo se declarase como parámetro, FastAPI lo parsearía y validaría
  antes de (o junto a) las dependencias, y una petición sin token con JSON inválido podría
  devolver 422 en lugar de 401. Con esta firma, la dependencia de autenticación se resuelve
  primero y garantiza el 401. Se cubre con una prueba específica (sin token + cuerpo inválido →
  401, IA no llamada).
- **Alternatives considered**: middleware de autenticación (afecta también a `/health` y a los
  preflight de CORS; más complejo de excluir); manejador global de `RequestValidationError`
  solo (no corrige el orden).

## R3. Cliente de la API de Gemini

- **Decision**: `httpx.AsyncClient` contra el endpoint compatible con OpenAI
  (`GEMINI_URL`, por defecto
  `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`), cabecera
  `Authorization: Bearer ${GEMINI_API_KEY}`, cuerpo `{model, messages:[system, user],
  max_tokens}`. Timeout total `AI_TIMEOUT_SECONDS` (25). Mapeo de errores:
  `httpx.TimeoutException` → 504 `TIMEOUT`; otros `httpx.HTTPError` o estado no 2xx → 502
  `IA_NO_DISPONIBLE`; JSON no parseable o `choices[0].message.content` ausente o en blanco →
  502 `RESPUESTA_INVALIDA`.
- **Rationale**: lo pide el equipo; httpx es asíncrono, tiene timeouts nativos y es fácil de
  sustituir por un doble en pruebas. El formato OpenAI es el que fija INT-02.
- **Alternatives considered**: SDK `google-genai` (otro formato, no el de INT-02); SDK `openai`
  apuntando a Gemini (dependencia innecesaria para una sola llamada).
- **Nota**: `GEMINI_MODEL` es configurable; su valor por defecto (`gemini-2.5-flash`) se
  comprueba contra los modelos disponibles en el plan gratuito al implementar.

## R4. Instrucciones a la IA

- **Decision**: mensaje de sistema fijo en el backend: recomendador musical, responder en
  español, entre 3 y 5 recomendaciones de artistas con una breve explicación de por qué encajan,
  texto plano sin HTML. Mensaje de usuario: el texto validado. No se envía ningún dato de
  identidad.
- **Rationale**: SUP-01 y RF-03; texto plano encaja con RF-04.

## R5. Variables de entorno (resuelve PEN-02)

**Backend** (`backend/.env`, nunca versionado; `backend/.env.example` con valores ficticios):

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `GEMINI_API_KEY` | Sí | — | Clave privada de la API de Gemini. |
| `GEMINI_URL` | No | `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` | Endpoint compatible con OpenAI. |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Modelo. |
| `MAX_TOKENS` | No | `800` | Máximo de tokens de respuesta. |
| `AI_TIMEOUT_SECONDS` | No | `25` | Tiempo máximo de espera a la IA. |
| `MAX_CARACTERES` | No | `500` | Longitud máxima de `tastes` tras recortar. |
| `CLERK_ISSUER` | Sí | — | Emisor de los tokens (Frontend API de Clerk, p. ej. `https://<instancia>.clerk.accounts.dev`). |
| `CLERK_JWKS_URL` | No | `${CLERK_ISSUER}/.well-known/jwks.json` | JWKS público del emisor. |
| `ALLOWED_ORIGINS` | Sí | — | Orígenes del frontend separados por comas (local, Vercel, EC2). Se usa para CORS y para el claim `azp`. |

No hay `CLERK_SECRET_KEY`: con la decisión R1 no se necesita. Si se cambiase al SDK oficial,
se añadiría solo en el backend.

**Frontend** (`frontend/.env`, nunca versionado; `frontend/.env.example`):

| Variable | Obligatoria | Uso |
|---|---|---|
| `VITE_CLERK_PUBLISHABLE_KEY` | Sí | Clave publishable de Clerk (única clave permitida en el frontend). |
| `VITE_API_URL` | No | URL base del backend. Vacía cuando el backend está en el mismo origen (EC2 tras el proxy); en Vercel, la URL del proyecto del backend. |

## R6. Frontend: Clerk en la misma pantalla

- **Decision**: Vue 3 + Vite + Tailwind CSS (plugin `@tailwindcss/vite`) y `@clerk/vue`
  (`clerkPlugin`, `<SignedIn>`, `<SignedOut>`, `<SignInButton mode="modal">`, `<UserButton>`,
  composable `useAuth()` para `isSignedIn` y `getToken()`). Sin `vue-router`.
- **Rationale**: SDK oficial para Vue; el modal evita rutas de login (principio VI). `getToken()`
  se llama antes de cada envío, así el token está siempre vigente.
- **Detalles**: el resultado se pinta con interpolación de texto (`{{ }}`) y
  `whitespace-pre-line`, nunca `v-html`. Al pasar `isSignedIn` a `false` se borran resultado y
  error. Composición de `tastes`: con géneros y texto → `Géneros: A, B. Además: texto`; solo
  géneros → `Géneros: A, B.`; solo texto → el texto tal cual.
- **Alternatives considered**: Clerk JS sin SDK de Vue (más código propio); página de login
  dedicada (prohibida por la ERS).

## R7. Géneros

- **Decision**: lista fija en el frontend, igual que App 1: Indie, Rock, Pop, Electrónica,
  Hip hop, Flamenco, Jazz, Metal, R&B, Reggaetón, Clásica, Lo-fi. Botones conmutables con
  `aria-pressed` y una marca visible (✓) además del color.
- **Rationale**: indicado por el equipo; RNF-04 exige no depender solo del color.

## R8. Pruebas

- **Decision**: pytest + `fastapi.testclient.TestClient`. La IA y el verificador se inyectan
  como dependencias de FastAPI (`get_ai_client`, `get_verifier`) y en las pruebas se sustituyen
  con `app.dependency_overrides` por dobles que registran sus llamadas. Las pruebas del
  verificador real usan un par RSA generado en la prueba y un `PyJWKClient` sustituido, sin red.
- **Rationale**: principio V; deterministas, sin claves reales y sin `pytest-asyncio`.

## R9. Despliegue en Vercel

- **Decision**: dos proyectos de Vercel desde el mismo repositorio. Frontend: raíz
  `app2-Musicfy/frontend`, build de Vite, salida `dist`. Backend: raíz `app2-Musicfy/backend`,
  runtime de Python con `api/index.py` que expone la `app` de FastAPI y `vercel.json` que
  reescribe todas las rutas a esa función, de modo que `/api/recommend` y `/health` se
  conservan. Variables de entorno configuradas en el panel de Vercel; HTTPS lo da Vercel.
- **Rationale**: frontend estático + backend serverless como pide la ERS; cada proyecto se
  despliega de forma independiente. Requiere CORS (`ALLOWED_ORIGINS`).

## R10. Despliegue en AWS EC2

- **Decision**: `docker compose` con dos servicios: `api` (imagen Python, `uvicorn`, puerto
  interno 8000, variables desde `backend/.env` en la instancia) y `web` (build multietapa: Node
  compila el frontend; Caddy sirve `dist`, hace `reverse_proxy` de `/api/*` y `/health` a
  `api:8000` y obtiene el certificado HTTPS automáticamente para el dominio). Solo se exponen
  80 y 443. `VITE_API_URL` vacía (mismo origen).
- **Rationale**: dos contenedores, HTTPS automático sin configurar certbot, sin servicios AWS
  extra (RES-11). El dominio depende de PEN-03.
- **Alternatives considered**: Nginx + certbot (más pasos manuales); exponer uvicorn
  directamente (sin HTTPS, incumple RNF-05).

## R11. Registros y errores

- **Decision**: manejador global de excepciones → 500 `ERROR_INTERNO`; los registros solo
  contienen el tipo de evento y el código de error, nunca `tastes`, el resultado, el token ni
  claves. `/health` responde `{"status": "ok"}`.
- **Rationale**: RF-05, RNF-03.
