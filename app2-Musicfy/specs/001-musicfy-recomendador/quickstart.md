# Quickstart: validar Musicfy App 2

Guía para comprobar que la funcionalidad cumple la especificación. Los detalles del contrato
están en [contracts/api.md](contracts/api.md) y [contracts/ui.md](contracts/ui.md); las
variables, en [research.md](research.md) (R5).

## Requisitos previos

- Python 3.12, Node.js 20 LTS o superior, Docker con `docker compose` (para EC2/local con
  contenedores).
- Una aplicación de Clerk con los orígenes local, Vercel y EC2 permitidos.
- Una clave de la API de Gemini (solo para pruebas manuales; las automáticas no la usan).

## 1. Pruebas automáticas (sin servicios reales)

```powershell
cd app2-Musicfy/backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest
```

Esperado: todas en verde, sin `.env` y sin red. Cubren PR-02 a PR-12 y PR-18 a PR-20, más:
sin token + cuerpo inválido → 401; `/health` sin token → 200.

## 2. Ejecución local

```powershell
# backend: copiar .env.example a .env y rellenar GEMINI_API_KEY, CLERK_ISSUER,
# ALLOWED_ORIGINS=http://localhost:5173
cd app2-Musicfy/backend; uvicorn app.main:app --reload --port 8000

# frontend: copiar .env.example a .env con VITE_CLERK_PUBLISHABLE_KEY y
# VITE_API_URL=http://localhost:8000
cd app2-Musicfy/frontend; npm install; npm run dev
```

Comprobaciones manuales (PR-13, PR-16, PR-17, PR-21):

1. Sin sesión: solo se ve el acceso de Clerk; el botón «Recomendar» está deshabilitado.
2. Iniciar sesión en el modal; elegir Jazz y escribir un texto; enviar → resultado en la misma
   pantalla. En F12, una sola petición con `tastes` y `Authorization`.
3. Pulsar varias veces durante la espera → una sola petición.
4. Enviar sin géneros ni texto → mensaje de validación y ninguna petición.
5. Cerrar sesión → el resultado desaparece y no se puede enviar.
6. `curl -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" -d '{"tastes":"rock"}'`
   → 401 `NO_AUTORIZADO`.
7. Teclado y vista de 320 px: todo alcanzable con foco visible y sin desplazamiento horizontal.

## 3. Comprobación de secretos (PR-14)

- `git ls-files | Select-String "\.env$"` → vacío (solo `.env.example`).
- Buscar el valor de `GEMINI_API_KEY` en `frontend/dist` y en `git log -p` → sin resultados.
- `docker history`/inspección de las imágenes → sin `.env`.

## 4. Vercel (PR-22)

Dos proyectos: frontend (raíz `app2-Musicfy/frontend`) y backend (raíz `app2-Musicfy/backend`).
Variables en el panel. Desde la URL del frontend: un caso válido con sesión y uno de error
(p. ej. 401 llamando al backend sin token). Anotar en `docs/despliegues.md`.

## 5. AWS EC2 (PR-15, PR-23)

```bash
# en la instancia, con backend/.env creado allí y DOMINIO apuntando a la IP
docker compose up -d --build
curl https://<dominio>/health        # {"status":"ok"}
docker compose down && docker compose up -d   # no queda historial
```

Desde otro dispositivo: acceso con Clerk, un caso válido y uno de error por HTTPS.
