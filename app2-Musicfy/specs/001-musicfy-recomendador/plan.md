# Implementation Plan: Musicfy App 2 — recomendador musical con IA y autenticación

**Branch**: `001-musicfy-recomendador` | **Date**: 2026-10-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-musicfy-recomendador/spec.md`

## Summary

Aplicación de una sola pantalla en la que un usuario con sesión de Clerk elige géneros y/o
describe sus gustos y recibe recomendaciones de la API de Gemini. El backend FastAPI expone
`POST /api/recommend` (y `GET /health`), verifica el JWT de Clerk con PyJWT + JWKS **antes** de
validar la entrada con Pydantic, hace una sola llamada con httpx al endpoint de Gemini
compatible con OpenAI y traduce cada fallo al contrato de errores fijo. El frontend Vue 3 +
Vite + Tailwind usa `@clerk/vue` en modo modal, sin router. Sin persistencia. Pruebas con pytest
sustituyendo la IA y el verificador mediante `dependency_overrides`. Despliegue en Vercel (dos
proyectos) y en EC2 con `docker compose` (API + Caddy con HTTPS).

## Technical Context

**Language/Version**: Python 3.12 (backend); JavaScript ES2022 con Node.js 22 LTS para el build (antes 20; ver la desviación de T035 en tasks.md)
(frontend).

**Primary Dependencies**: backend: FastAPI, Pydantic v2, httpx, PyJWT[crypto], uvicorn.
Frontend: Vue 3, Vite, Tailwind CSS (`@tailwindcss/vite`), `@clerk/vue`.

**Storage**: N/A (prohibido por el principio II).

**Testing**: pytest + `fastapi.testclient.TestClient`; dobles de la IA y del verificador
inyectados con `app.dependency_overrides`; tokens firmados localmente para las pruebas del
verificador real. Frontend: pruebas manuales PR-16, PR-17, PR-21.

**Target Platform**: navegadores actuales de escritorio y móvil; backend en Linux (función
serverless de Vercel y contenedor Docker en EC2).

**Project Type**: aplicación web (frontend SPA + backend API).

**Performance Goals**: sin objetivos de rendimiento propios (volumen de demostración, ERS 2.4).
Límite de espera a la IA: 25 s.

**Constraints**: una pantalla, un formulario, una ruta funcional; `tastes` ≤ 500 caracteres;
`MAX_TOKENS` limitado; HTTPS en despliegues; sin secretos en el frontend; plan gratuito de
Gemini.

**Scale/Scope**: 1 pantalla, 2 rutas de backend, ~6 módulos de backend, ~3 ficheros Vue.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento en el plan | Estado |
|---|---|---|
| I. Secretos solo en el backend | `GEMINI_API_KEY` solo en `backend/.env`/panel de Vercel/instancia EC2. Frontend solo `VITE_CLERK_PUBLISHABLE_KEY`. Ni siquiera hace falta `CLERK_SECRET_KEY` (R1). `.env` en `.gitignore` y `.dockerignore`; solo `.env.example`. Errores y registros sin claves ni tokens (R11). | ✅ |
| II. Sin persistencia | Sin base de datos, sin escritura en disco, sin almacenamiento del navegador; el resultado se borra al cerrar sesión. | ✅ |
| III. Contrato fijo | `contracts/api.md` reproduce exactamente el contrato y los códigos; una llamada a la IA por petición válida. | ✅ |
| IV. Autenticación antes que todo | El endpoint no declara el cuerpo como parámetro; `require_session` se resuelve antes de leer y validar (R2). Verificación de firma, `iss`, `exp`/`nbf` y `azp` con JWKS (R1). Prueba explícita sin token + cuerpo inválido → 401. | ✅ |
| V. Pruebas sin servicios reales | Dobles por `dependency_overrides`; verificador real probado con claves RSA locales y JWKS sustituido; ningún acceso a red (R8). | ✅ |
| VI. Alcance mínimo | Solo `POST /api/recommend` y `GET /health`; sin router; acceso de Clerk en modal; ninguna función fuera de la ERS. | ✅ |
| Restricciones técnicas | Vue + Tailwind, FastAPI, Gemini (formato OpenAI), Clerk, Vercel y EC2/Docker con HTTPS; resultado sin `v-html`; CORS limitado a `ALLOWED_ORIGINS`. | ✅ |
| Flujo de desarrollo | Spec, plan y tareas se versionan antes del código; no se copia App 1. | ✅ (a cumplir en `/speckit-tasks` e implementación) |

**Resultado (antes de la fase 0)**: superado, sin violaciones.
**Resultado (tras la fase 1)**: superado. El diseño no añade rutas, almacenamiento ni secretos
en el frontend; Caddy en EC2 es parte del despliegue obligatorio con HTTPS, no una función.

## Project Structure

### Documentation (this feature)

```text
specs/001-musicfy-recomendador/
├── plan.md              # Este fichero
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── api.md           # Contrato HTTP
│   └── ui.md            # Contrato de la pantalla
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
app2-Musicfy/
├── .gitignore                 # .env, .venv, node_modules, dist, __pycache__
├── docker-compose.yml         # servicios api + web (EC2)
├── backend/
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt   # + pytest
│   ├── vercel.json            # reescribe todo a /api/index
│   ├── api/
│   │   └── index.py           # expone app para Vercel
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI, CORS, rutas, manejadores de error
│   │   ├── config.py          # Settings desde variables de entorno
│   │   ├── errors.py          # ApiError, códigos y mensajes del contrato
│   │   ├── auth.py            # ClerkVerifier (PyJWT + JWKS), require_session
│   │   ├── schemas.py         # RecommendRequest, RecommendResponse, ErrorResponse
│   │   └── ai_client.py       # GeminiClient (httpx) y prompt del recomendador
│   └── tests/
│       ├── conftest.py        # cliente, dobles de IA y verificador
│       ├── test_health.py     # PR-01
│       ├── test_auth.py       # PR-18..20, 401 antes que 422, verificador real con RSA local
│       ├── test_validation.py # PR-02..05, PR-07, PR-08
│       ├── test_recommend.py  # PR-06, PR-09
│       └── test_ai_errors.py  # PR-10..12, 500
└── frontend/
    ├── .env.example
    ├── .dockerignore
    ├── Dockerfile             # build Node + Caddy
    ├── Caddyfile              # estáticos, proxy /api y /health, HTTPS
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js            # createApp + clerkPlugin
        ├── style.css          # @import "tailwindcss"
        ├── App.vue            # pantalla única: acceso, formulario, estados
        └── api.js             # composeTastes() y recommend(tastes, token)
```

**Structure Decision**: aplicación web con `app2-Musicfy/backend` y `app2-Musicfy/frontend`,
como pidió el equipo. El backend separa configuración, autenticación, cliente de IA y errores
para poder sustituir la IA y el verificador en pruebas; el frontend se limita a un componente
de pantalla y un módulo de llamada, sin router.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
