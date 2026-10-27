---

description: "Task list for Musicfy App 2 implementation"
---

# Tasks: Musicfy App 2 — recomendador musical con IA y autenticación

**Input**: Design documents from `/specs/001-musicfy-recomendador/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, contracts/ui.md, quickstart.md

**Tests**: SÍ. La ERS (RES-06, sección 8) y la constitución (principio V) exigen pruebas pytest
con la IA y el verificador de Clerk simulados. Las pruebas de cada historia se escriben primero y
deben fallar antes de implementar.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4 de spec.md)
- Rutas relativas a `app2-Musicfy/` (raíz del proyecto Spec Kit).

## Reglas que aplican a todas las tareas

- Nunca registrar ni devolver `tastes`, el resultado, el token ni claves (principios I y II).
- Nada de base de datos, ficheros, `localStorage`, `sessionStorage` ni IndexedDB.
- Ninguna ruta, pantalla ni función que no esté en `contracts/api.md` o `contracts/ui.md`.
- Mensajes de error copiados literalmente de `contracts/api.md`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `.gitignore` in the project root ignoring `.env`, `*.env.local`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/` and `dist/` (keep `.env.example` tracked)
- [X] T002 [P] Create `backend/requirements.txt` (fastapi, pydantic v2, httpx, pyjwt[crypto], uvicorn[standard]; pin current stable versions) and `backend/requirements-dev.txt` (`-r requirements.txt` + pytest)
- [X] T003 [P] Create `backend/pytest.ini` with `testpaths = tests` and `pythonpath = .`, plus empty `backend/app/__init__.py`
- [X] T004 [P] Create `backend/.env.example` with every variable of research.md R5 and fictitious values: `GEMINI_API_KEY=tu-clave-aqui`, `GEMINI_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`, `GEMINI_MODEL=gemini-3.5-flash-lite`, `MAX_TOKENS=600`, `AI_TIMEOUT_SECONDS=25`, `MAX_CARACTERES=500`, `CLERK_ISSUER=https://tu-instancia.clerk.accounts.dev`, `CLERK_JWKS_URL=` (vacío = `${CLERK_ISSUER}/.well-known/jwks.json`), `ALLOWED_ORIGINS=http://localhost:5173`
- [X] T005 [P] Scaffold the frontend: `frontend/package.json` (vue 3, @clerk/vue, vite, @vitejs/plugin-vue, tailwindcss, @tailwindcss/vite; scripts `dev`, `build`, `preview`), `frontend/vite.config.js` (plugins vue + tailwindcss), `frontend/index.html` (`lang="es"`, viewport meta, `<div id="app">`) and `frontend/src/style.css` containing `@import "tailwindcss";`
- [X] T006 [P] Create `frontend/.env.example` with `VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxx` and `VITE_API_URL=http://localhost:8000` (no other keys allowed in the frontend)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configuración, errores, esquemas, verificación de Clerk y esqueleto de la app que necesitan todas las historias

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Implement `backend/app/config.py`: `Settings` read from environment variables (research.md R5) with defaults `GEMINI_URL`, `GEMINI_MODEL=gemini-3.5-flash-lite`, `MAX_TOKENS=600`, `AI_TIMEOUT_SECONDS=25`, `MAX_CARACTERES=500`; `CLERK_JWKS_URL` defaults to `f"{CLERK_ISSUER}/.well-known/jwks.json"`; `ALLOWED_ORIGINS` parsed as a comma-separated list (trimmed, empty items dropped); `get_settings()` cached with `functools.lru_cache`; missing required variables MUST NOT crash at import time
- [X] T008 [P] Implement `backend/app/errors.py`: `ApiError(Exception)` with `status_code`, `codigo`, `mensaje`; factory helpers `no_autorizado()` (401), `validacion(max_caracteres)` (422, «Describe tus gustos musicales (entre 1 y {max_caracteres} caracteres).»), `timeout()` (504), `ia_no_disponible()` (502), `respuesta_invalida()` (502), `error_interno()` (500), with the exact Spanish messages of contracts/api.md; `error_body(err)` returns `{"error": {"codigo": ..., "mensaje": ...}}`
- [X] T009 [P] Implement `backend/app/schemas.py`: `RecommendRequest` with `tastes: StrictStr` — "Obligatorio. Se recortan espacios iniciales y finales; tras recortar, longitud entre 1 y `MAX_CARACTERES` (500)"; extra fields ignored; plus a function `validate_tastes(payload, max_caracteres) -> str` that returns the trimmed text or raises `errors.validacion(...)` for: payload not a dict, missing `tastes`, non-string, empty or only spaces, length > max after trimming. Also `RecommendResponse(resultado: str)` and `ErrorResponse` models for documentation
- [X] T010 Implement `backend/app/auth.py`: class `ClerkVerifier(issuer, jwks_url, allowed_origins)` using `jwt.PyJWKClient(jwks_url)` (cached) and `jwt.decode(token, key, algorithms=["RS256"], issuer=issuer, leeway=5, options={"require": ["exp", "iss"]})`; if claim `azp` exists it MUST be in `allowed_origins`; ANY exception (PyJWT errors, JWKS fetch failure, missing issuer config) raises `errors.no_autorizado()`; dependency `get_verifier()` builds it from settings; dependency `require_session(request: Request, verifier = Depends(get_verifier))` reads `Authorization`, requires scheme `Bearer` + non-empty token, calls `verifier.verify(token)`, never logs the token (depends on T007, T008)
- [X] T011 [P] Create `backend/app/ai_client.py` skeleton: `AIClient` protocol with `async def recommend(self, tastes: str) -> str`, class `GeminiClient(settings, transport=None)` (body implemented in US1/US4), and dependency `get_ai_client()` returning a `GeminiClient` built from settings
- [X] T012 Implement `backend/app/main.py` skeleton: `app = FastAPI(title="Musicfy")`; `CORSMiddleware` with `allow_origins=settings.ALLOWED_ORIGINS`, `allow_methods=["GET","POST","OPTIONS"]`, `allow_headers=["Authorization","Content-Type"]`, `allow_credentials=False`; exception handlers: `ApiError` → its status + `error_body`, `RequestValidationError` → 422 VALIDACION, `Exception` → 500 ERROR_INTERNO (log only the error code/type, never request data); `GET /health` → `{"status": "ok"}` without auth (depends on T007–T011)
- [X] T013 Create `backend/tests/conftest.py`: `FakeVerifier` (accepts token `"valido"`, raises `no_autorizado()` otherwise, records calls); `FakeAIClient` (configurable return text or exception, records each `tastes` received in `.calls`); fixtures `fake_ai`, `fake_verifier`, `client` (TestClient with `app.dependency_overrides` for `get_verifier` and `get_ai_client`, cleared after each test) and `auth_header = {"Authorization": "Bearer valido"}`; no test may need `.env` or network
- [X] T014 [P] Write `backend/tests/test_health.py` (PR-01): `GET /health` without token → 200 `{"status": "ok"}`
- [X] T015 [P] Implement `frontend/src/main.js`: `createApp(App).use(clerkPlugin, { publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY }).mount('#app')` and import `./style.css`; create `frontend/src/App.vue` shell with a single-column `<main>` and the heading «Musicfy» (no router, no other pages)

**Checkpoint**: `python -m pytest` passes (health); frontend arranca con `npm run dev`

---

## Phase 3: User Story 1 - Obtener recomendaciones con la sesión iniciada (Priority: P1) 🎯 MVP

**Goal**: con sesión válida, enviar géneros y/o texto y ver el resultado de una única consulta a la IA en la misma pantalla

**Independent Test**: con verificador e IA simulados, `POST /api/recommend` con token válido y texto válido → 200 con el resultado simulado y una sola llamada a la IA con el texto recortado; en la pantalla, el resultado aparece sin navegar y sustituye al anterior

### Tests for User Story 1 ⚠️

- [X] T016 [P] [US1] Write `backend/tests/test_recommend.py`: PR-06 (token válido + `{"tastes": "Rock y jazz tranquilo"}` → 200 `{"resultado": <texto del fake>}`, `len(fake_ai.calls) == 1`, `fake_ai.calls[0] == "Rock y jazz tranquilo"`); PR-09 (`"  indie  "` → la IA recibe `"indie"`); campos extra en el cuerpo se ignoran → 200

### Implementation for User Story 1

- [X] T017 [US1] Implement the success path of `GeminiClient.recommend` in `backend/app/ai_client.py`: `httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS, transport=transport)`; `POST settings.GEMINI_URL` with header `Authorization: Bearer {GEMINI_API_KEY}` and JSON `{"model": GEMINI_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": tastes}], "max_tokens": MAX_TOKENS}`; return `choices[0].message.content.strip()`. `SYSTEM_PROMPT` (research.md R4): recomendador musical, responde en español con entre 3 y 5 artistas y una breve explicación de por qué encajan, texto plano sin HTML ni Markdown. Never send identity data
- [X] T018 [US1] Add `POST /api/recommend` in `backend/app/main.py` with signature `async def recommend(request: Request, _=Depends(require_session), ai=Depends(get_ai_client))` — do NOT declare a body parameter (research.md R2, so auth runs first); then `payload = await request.json()` (JSON error → `validacion`), `tastes = validate_tastes(payload, settings.MAX_CARACTERES)`, `resultado = await ai.recommend(tastes)` exactly once, return `{"resultado": resultado}`
- [X] T019 [P] [US1] Implement `frontend/src/api.js`: export `GENEROS = ["Indie","Rock","Pop","Electrónica","Hip hop","Flamenco","Jazz","Metal","R&B","Reggaetón","Clásica","Lo-fi"]`; `composeTastes(generos, texto)` following data-model.md (géneros + texto → `Géneros: A, B. Además: <texto>`; solo géneros → `Géneros: A, B.`; solo texto → el texto recortado; nada → `""`); `recommend(tastes, token)` doing `fetch(\`${import.meta.env.VITE_API_URL ?? ""}/api/recommend\`, {method: "POST", headers: {"Content-Type": "application/json", Authorization: \`Bearer ${token}\`}, body: JSON.stringify({tastes})})` and returning `{ status, data }` (network failure → `{ status: 0, data: null }`)
- [X] T020 [US1] Build the form in `frontend/src/App.vue` (contracts/ui.md): `<div role="group" aria-label="Géneros musicales">` with one `<button type="button">` per `GENEROS` toggling selection, `:aria-pressed`, and a visible «✓» when selected; `<label for="gustos">¿Qué música te gusta?</label>` + `<textarea id="gustos">`; button «Recomendar» disabled while `cargando`; on submit get a fresh token with `useAuth().getToken.value()`, set `cargando=true`, call `recommend`, on 200 set `resultado` (replacing any previous one) and clear `error`, on error set `error = data?.error?.mensaje`; ignore submits while `cargando`; loading indicator with `aria-live="polite"`; result rendered with `{{ resultado }}` inside a container with `whitespace-pre-line break-words` — never `v-html`

**Checkpoint**: US1 funcional y probada de forma independiente (pytest + demostración con sesión)

---

## Phase 4: User Story 2 - Iniciar y cerrar sesión y proteger el servicio (Priority: P1)

**Goal**: acceso de Clerk en modal en la misma pantalla; sin sesión no se envía; el backend rechaza con 401 toda petición sin token válido sin llamar a la IA

**Independent Test**: con el verificador simulado, peticiones sin token, con token inválido, caducado o con cuerpo inválido → 401 `NO_AUTORIZADO` y `fake_ai.calls == []`; el verificador real rechaza tokens con firma, emisor, caducidad o `azp` incorrectos usando claves locales

### Tests for User Story 2 ⚠️

- [X] T021 [P] [US2] Write `backend/tests/test_auth.py`: PR-18 `test_sin_token_da_401` (sin cabecera → 401, body exactamente `{"error": {"codigo": "NO_AUTORIZADO", "mensaje": "Tu sesión no es válida o ha caducado. Inicia sesión de nuevo."}}`, IA no llamada); PR-19 `test_token_invalido_da_401` (`Bearer otro` → 401, IA no llamada); PR-20 `test_token_caducado_da_401` (fake configurado para simular caducidad → 401, IA no llamada); esquema distinto de `Bearer` → 401; `Bearer ` vacío → 401; sin token y cuerpo `{}` o no JSON → 401 (no 422) e IA no llamada
- [X] T022 [P] [US2] Write `backend/tests/test_clerk_verifier.py` for the real `ClerkVerifier` without network: generate an RSA key with `cryptography`, sign tokens with PyJWT (RS256, `kid`), monkeypatch `PyJWKClient.get_signing_key_from_jwt` to return the public key; cases: válido (iss correcto, exp futuro, azp permitido) → pasa; firma con otra clave → 401; `iss` distinto → 401; `exp` pasado → 401; `azp` no incluido en `ALLOWED_ORIGINS` → 401; token mal formado → 401; fallo al obtener el JWKS → 401

### Implementation for User Story 2

- [X] T023 [US2] Add Clerk access to `frontend/src/App.vue` using `@clerk/vue`: inside `<SignedOut>` a `<SignInButton mode="modal">` (botón «Iniciar sesión»); inside `<SignedIn>` a `<UserButton />`; the «Recomendar» button disabled when `!isSignedIn || cargando`; no routes or extra pages
  - **Desviación (2026-10-27)**: @clerk/vue 2.x ya no incluye `<SignedIn>` ni `<SignedOut>`; se usa su sustituto `<Show when="signed-out">` y `<Show when="signed-in">`, con el mismo comportamiento. `SignInButton` recibe un botón propio «Iniciar sesión» porque sin él muestra «Sign in».
- [X] T024 [US2] In `frontend/src/App.vue`, `watch(isSignedIn)` so that when it becomes `false` it clears `resultado`, `error` and `cargando` (CA-RF04-04); when the backend answers 401, show `error.mensaje` plus the invitation «Inicia sesión de nuevo para continuar.»
- [X] T025 [US2] Review `backend/app/auth.py` and `backend/app/main.py` against the tests T021–T022 and fix until they pass; confirm `/health` stays public and that `require_session` is the first dependency of `/api/recommend`

**Checkpoint**: US1 y US2 funcionan; ninguna petición sin sesión llega a la IA

---

## Phase 5: User Story 3 - Rechazar entradas no válidas sin consultar a la IA (Priority: P2)

**Goal**: aviso local con el formulario vacío; 422 `VALIDACION` en el backend para entradas inválidas sin llamar a la IA

**Independent Test**: con token válido simulado, los casos límite devuelven 422 (o 200 en el límite exacto) y `fake_ai.calls` queda vacío en los rechazos

### Tests for User Story 3 ⚠️

- [X] T026 [P] [US3] Write `backend/tests/test_validation.py` (token válido en todos): PR-02 `""` → 422 `VALIDACION` con el mensaje exacto de contracts/api.md; PR-08 en ese caso `fake_ai.calls == []`; PR-03 `"   "` → 422; PR-04 `{}` → 422; PR-05 `"a" * 501` → 422; PR-07 `"a" * 500` → 200; `"  " + "a"*500 + "  "` → 200 (se cuenta tras recortar); `{"tastes": 123}` → 422; cuerpo no JSON → 422; cuerpo JSON que es una lista → 422; con `MAX_CARACTERES=10` (override de settings) `"a"*11` → 422 y el mensaje dice 10

### Implementation for User Story 3

- [X] T027 [US3] Make `backend/app/schemas.py` (`validate_tastes`) and `backend/app/main.py` pass T026 without changing the processing order (auth → validación → IA)
- [X] T028 [US3] In `frontend/src/App.vue`, before requesting a token, if `composeTastes(...)` is `""` show exactly «Elige algún género o escribe algo sobre la música que te gusta» and send nothing (CA-RF01-04); clear that message on the next valid submit

**Checkpoint**: US1–US3 funcionan de forma independiente

---

## Phase 6: User Story 4 - Informar de fallos de la IA de forma comprensible (Priority: P2)

**Goal**: 504 `TIMEOUT`, 502 `IA_NO_DISPONIBLE`, 502 `RESPUESTA_INVALIDA` y 500 `ERROR_INTERNO` con el formato del contrato, sin detalles internos, y mensaje visible en la pantalla

**Independent Test**: con la IA simulada fallando de cada forma, el backend devuelve el código exacto y el cuerpo exacto del contrato; `GeminiClient` traduce cada fallo de httpx usando `httpx.MockTransport`

### Tests for User Story 4 ⚠️

- [X] T029 [P] [US4] Write `backend/tests/test_ai_errors.py` (token válido, entrada válida): PR-10 fake lanza `errors.timeout()` → 504 `TIMEOUT`; PR-11 fake lanza `errors.ia_no_disponible()` → 502 `IA_NO_DISPONIBLE`; PR-12 fake lanza `errors.respuesta_invalida()` → 502 `RESPUESTA_INVALIDA`; fake lanza `RuntimeError("secreto-interno")` → 500 `ERROR_INTERNO` y el cuerpo no contiene `secreto-interno` ni `Traceback`; en todos, el cuerpo es exactamente `{"error": {"codigo", "mensaje"}}`
- [X] T030 [P] [US4] Write `backend/tests/test_gemini_client.py` using `httpx.MockTransport` (no network): 200 con `choices[0].message.content = "  Texto  "` → `"Texto"`; la petición lleva `Authorization: Bearer <clave de prueba>`, `model`, `max_tokens` y dos mensajes (system, user = tastes) y nada más del usuario; `httpx.ReadTimeout` → `TIMEOUT`; `httpx.ConnectError` → `IA_NO_DISPONIBLE`; estado 429/500 → `IA_NO_DISPONIBLE`; 200 con contenido vacío, sin `choices` o cuerpo no JSON → `RESPUESTA_INVALIDA`; `GEMINI_API_KEY` vacía → `IA_NO_DISPONIBLE` sin hacer la petición

### Implementation for User Story 4

- [X] T031 [US4] Add error mapping to `GeminiClient.recommend` in `backend/app/ai_client.py`: `httpx.TimeoutException` → `errors.timeout()`; other `httpx.HTTPError` or non-2xx status → `errors.ia_no_disponible()`; unparseable JSON, missing `choices[0].message.content`, non-string or blank content → `errors.respuesta_invalida()`; missing `GEMINI_API_KEY` → `errors.ia_no_disponible()`; never include the provider response in the error
- [X] T032 [US4] In `frontend/src/App.vue`, show `data.error.mensaje` for any non-200 response and, when `status === 0` or the body has no `error`, show «No se puede conectar con el servicio. Inténtalo más tarde.»; long messages wrap without horizontal scroll

**Checkpoint**: todas las historias funcionan; `python -m pytest` en verde

---

## Phase 7: Polish & Cross-Cutting Concerns (despliegue y verificación)

**Purpose**: despliegue en Vercel y EC2 con HTTPS, accesibilidad y comprobaciones de seguridad

- [X] T033 [P] Create `backend/api/index.py` (`from app.main import app`) and `backend/vercel.json` rewriting `/(.*)` to `/api/index` so `/api/recommend` and `/health` keep their paths in Vercel (research.md R9)
- [X] T034 [P] Create `backend/Dockerfile` (python:3.12-slim, install `requirements.txt`, copy `app/`, `CMD uvicorn app.main:app --host 0.0.0.0 --port 8000`) and `backend/.dockerignore` (`.env`, `.venv`, `tests`, `__pycache__`, `.pytest_cache`)
- [X] T035 [P] Create `frontend/Dockerfile` (stage 1 node:20 with `ARG VITE_CLERK_PUBLISHABLE_KEY` and `ARG VITE_API_URL=""`, `npm ci && npm run build`; stage 2 `caddy:2` copying `dist` to `/srv` and `Caddyfile`), `frontend/Caddyfile` (`{$DOMINIO} { handle /api/* { reverse_proxy api:8000 } handle /health { reverse_proxy api:8000 } handle { root * /srv; try_files {path} /index.html; file_server } }`) and `frontend/.dockerignore` (`.env`, `node_modules`, `dist`)
  - **Desviación (2026-10-27)**: la etapa 1 usa `node:22` en lugar de `node:20`, porque Node 20 dejó de tener soporte en abril de 2026 y Vite 8 funciona con Node 22. Solo afecta a la imagen de compilación; `plan.md` ya dice Node.js 22 LTS.
- [X] T036 Create `docker-compose.yml` in the project root: service `api` (build `./backend`, `env_file: ./backend/.env`, `expose: ["8000"]`, `restart: unless-stopped`); service `web` (build `./frontend` with build args from the host environment, `environment: DOMINIO`, ports `80:80` and `443:443`, volume `caddy_data:/data` only for TLS certificates); no other services (research.md R10)
- [X] T037 Accessibility pass in `frontend/src/App.vue` (RNF-04, PR-17): `focus-visible` ring on every button, textarea and Clerk button; selected genre distinguishable without color (✓ + `aria-pressed`); `max-w` single column with padding and no fixed widths so there is no horizontal scroll at 320 px
- [X] T038 Security review (PR-14, RNF-03): search `backend/app/` for any logging of `tastes`, `resultado`, tokens or keys and remove it; confirm `.env` is ignored by `.gitignore` and both `.dockerignore`; confirm `frontend/src` only reads `VITE_CLERK_PUBLISHABLE_KEY` and `VITE_API_URL`; confirm no `v-html`, `localStorage`, `sessionStorage` or IndexedDB in `frontend/src`
- [X] T039 Run `python -m pytest` in `backend/` and fix any failure until all tests pass
- [X] T040 Run the manual validation of `specs/001-musicfy-recomendador/quickstart.md` sections 2 and 3 (PR-13, PR-16, PR-17, PR-21, PR-14) and record the results in the team's test log (`../docs/pruebas.md` per the ERS)
- [ ] T041 Deploy to Vercel (two projects, quickstart.md §4) and to EC2 (quickstart.md §5) and record URLs and the valid/error cases in `../docs/despliegues.md` (PR-22, PR-23, PR-15; resolves PEN-06)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende de Setup; BLOQUEA todas las historias. Orden interno: T007, T008, T009, T011 en paralelo → T010 → T012 → T013 → T014, T015
- **US1 (Phase 3)** y **US2 (Phase 4)**: dependen de Foundational; pueden avanzar en paralelo (backend de US2 ya está en Foundational; su frontend toca `App.vue` después de T020)
- **US3 (Phase 5)** y **US4 (Phase 6)**: dependen de T018 (endpoint) de US1
- **Polish (Phase 7)**: tras las historias deseadas; T033–T035 pueden empezar antes

### User Story Dependencies

- **US1 (P1)**: tras Foundational. MVP
- **US2 (P1)**: tras Foundational; las tareas de frontend T023–T024 editan `App.vue` tras T020
- **US3 (P2)**: necesita el endpoint de T018; T028 edita `App.vue` tras T020
- **US4 (P2)**: necesita T017–T018; T032 edita `App.vue` tras T020

### Within Each User Story

- Pruebas primero (deben fallar) → backend → frontend
- Las tareas que editan `frontend/src/App.vue` (T020, T023, T024, T028, T032, T037) son secuenciales

---

## Parallel Example: Foundational + User Story 1

```text
# Foundational, en paralelo:
Task: "T007 Settings in backend/app/config.py"
Task: "T008 ApiError and messages in backend/app/errors.py"
Task: "T009 RecommendRequest and validate_tastes in backend/app/schemas.py"
Task: "T011 AIClient skeleton in backend/app/ai_client.py"

# User Story 1, en paralelo:
Task: "T016 tests in backend/tests/test_recommend.py"
Task: "T019 GENEROS, composeTastes and recommend in frontend/src/api.js"
```

## Parallel Example: tests de US2–US4

```text
Task: "T021 backend/tests/test_auth.py"
Task: "T022 backend/tests/test_clerk_verifier.py"
Task: "T026 backend/tests/test_validation.py"
Task: "T029 backend/tests/test_ai_errors.py"
Task: "T030 backend/tests/test_gemini_client.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational (incluye la verificación del token: el MVP ya está protegido)
3. Phase 3: US1
4. **STOP and VALIDATE**: `python -m pytest` + demostración local con sesión real
5. Continuar con US2 (acceso de Clerk en pantalla)

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 → MVP de recomendación
3. US2 → acceso de Clerk y 401 completos
4. US3 → validaciones
5. US4 → errores de la IA
6. Polish → Docker, Vercel, EC2, accesibilidad y seguridad

### Parallel Team Strategy (tres integrantes)

1. Todo el equipo: Setup + Foundational
2. Después: A → US1 + US4 (backend IA); B → US2 + US3 (tests de auth y validación); C → frontend (`api.js`, luego `App.vue` en orden T020 → T023 → T024 → T028 → T032) y Phase 7 (Docker/Vercel)

---

## Notes

- [P] = ficheros distintos y sin dependencias pendientes
- Hacer commit tras cada tarea o grupo lógico; la especificación, el plan y estas tareas deben estar en Git antes del código (RES-09)
- Ninguna prueba puede usar claves reales ni red
- Si una tarea requiere algo fuera de la ERS, parar y enmendar primero la ERS (principio VI)
