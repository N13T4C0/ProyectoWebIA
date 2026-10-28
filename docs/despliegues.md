# Despliegues de Musicfy

Este documento recoge cómo se despliega cada aplicación, sus variables de entorno (solo los nombres, nunca los valores) y las comprobaciones hechas tras desplegar. Las capturas están en `docs/evidencias/`.

## App 1 en Vercel

**URL:** https://proyectowebia.vercel.app/

**Responsable:** Jose Antonio Nieto

### Arquitectura

Un único proyecto de Vercel conectado al repositorio, con dos servicios definidos en `vercel.json` (raíz del repositorio):

| Servicio | Carpeta | Tipo |
|---|---|---|
| `frontend` | `app1-Musicfy/frontend` | Vite (SPA en Vue.js) |
| `backend` | `app1-Musicfy/backend` | FastAPI (función serverless) |

Una regla de reescritura envía `/api/*` al backend y el resto de rutas al frontend. Así la aplicación tiene una sola URL y el frontend llama a la API con una ruta relativa (`/api/recommend`), sin necesidad de CORS en producción.

### Variables de entorno

Se configuran en el panel de Vercel (*Settings → Environment Variables*). Ninguna clave está en el repositorio: solo se versionan los `.env.example`.

| Variable | Servicio | Uso |
|---|---|---|
| `GEMINI_API_KEY` | Backend | Clave de la API de Gemini (secreta). |
| `GEMINI_URL` | Backend | Endpoint de Gemini compatible con OpenAI. |
| `GEMINI_MODEL` | Backend | Modelo de IA (`gemini-3.5-flash-lite`). |
| `MAX_TOKENS` | Backend | Máximo de tokens de respuesta (600). |
| `MAX_CARACTERES` | Backend | Longitud máxima de `tastes` (500). |
| `AI_TIMEOUT_SECONDS` | Backend | Tiempo máximo de espera a la IA (25 s). |
| `ALLOWED_ORIGINS` | Backend | Orígenes permitidos por CORS (solo necesario en local). |
| `VITE_API_BASE_URL` | Frontend | URL del backend. En producción se deja vacía y se usa la ruta relativa `/api`. |
| `VITE_USE_MOCK` | Frontend | `false` en producción (`true` solo para desarrollar sin backend). |

### Pasos para desplegar

1. En Vercel, *Add New → Project* e importar el repositorio `N13T4C0/ProyectoWebIA` desde GitHub.
2. Dejar como raíz la del repositorio: Vercel lee `vercel.json` y crea los servicios `frontend` y `backend`.
3. Añadir las variables de entorno de la tabla anterior.
4. Pulsar *Deploy*. Cada `git push` a `main` vuelve a desplegar automáticamente.

**Limitación del plan gratuito (Hobby):** en un repositorio privado, Vercel solo despliega los commits del propietario del proyecto; los commits de otros integrantes aparecen como bloqueados. No afecta a la versión publicada, que sigue siendo la del último despliegue correcto.

### Comprobaciones

| Fecha | Caso | Cómo | Resultado | Evidencia |
|---|---|---|---|---|
| 28/10/2026 | Válido | En la pantalla: géneros Electrónica, Flamenco y Metal, y el texto «Me gusta la musica de los 2000s». | 200: la pantalla muestra las recomendaciones de artistas. | `evidencias/app1-vercel-valido.png` |
| 28/10/2026 | Error | Desde la consola del navegador: `POST /api/recommend` con `{"tastes": ""}`. | 422 con `{"error": {...}}` de validación, sin consultar a la IA. | `evidencias/app1-vercel-error.png` |

### Evidencia con la CLI de Vercel

Comprobación hecha el 28/10/2026 con Vercel CLI 65.5.0 (Node.js 22.20.0), desde `app2-Musicfy/backend`. Vercel detecta el repositorio y enlaza el proyecto conectado a Git, que es el de la App 1 (`proyectowebia`).

```
npm install -g vercel
vercel --version
vercel login
vercel link     # proyecto proyectowebia (linked by git)
vercel env ls   # nombres de las variables; los valores salen cifrados u ocultos
vercel ls       # despliegues de producción y su estado
```

Resultado:

- `vercel env ls` muestra las siete variables del backend (`GEMINI_API_KEY`, `GEMINI_URL`, `GEMINI_MODEL`, `MAX_TOKENS`, `MAX_CARACTERES`, `AI_TIMEOUT_SECONDS` y `ALLOWED_ORIGINS`) en *Preview* y *Production*. `GEMINI_API_KEY` y `MAX_TOKENS` están como *Secret*, con el valor oculto.
- `vercel ls` muestra los despliegues de producción en estado *Ready*. Los que aparecen como *Blocked* son commits de otros integrantes; los bloquea el plan Hobby, como se explica arriba.
- `vercel link` crea `.vercel/` y `.env.local` (con un token temporal de Vercel). Los dos están excluidos en `.gitignore`. La CLI también añadió `.env*` al `.gitignore`; se deshizo ese cambio porque anulaba la excepción `!.env.example`.

Evidencia: `evidencias/vercel-cli.png`.

## App 2

### Vercel

**URL:** https://musicfy-app2.vercel.app/ (frontend) · https://musicfy-app2-api.vercel.app/ (backend)

**Responsable:** Jose Antonio Nieto

#### Arquitectura

Dos proyectos de Vercel conectados al mismo repositorio, como fija el plan de Spec Kit:

| Proyecto | Carpeta raíz | Tipo |
|---|---|---|
| `musicfy-app2` | `app2-Musicfy/frontend` | Vite (SPA en Vue.js con Clerk) |
| `musicfy-app2-api` | `app2-Musicfy/backend` | FastAPI (función serverless, Python 3.12) |

El frontend llama al backend por su URL completa (`VITE_API_URL`), así que el backend debe permitir el origen del frontend en CORS (`ALLOWED_ORIGINS`). Ese mismo valor se usa para comprobar el campo `azp` del token de Clerk.

#### Variables de entorno

| Variable | Proyecto | Uso |
|---|---|---|
| `GEMINI_API_KEY` | Backend | Clave de la API de Gemini (secreta). |
| `GEMINI_MODEL` | Backend | Modelo de IA (`gemini-3.5-flash-lite`). |
| `MAX_TOKENS` | Backend | Máximo de tokens de respuesta (600). |
| `CLERK_ISSUER` | Backend | Emisor de los tokens de Clerk; el backend obtiene de él las claves públicas (JWKS). |
| `ALLOWED_ORIGINS` | Backend | Orígenes permitidos: la URL del frontend en Vercel (y `http://localhost:5173` para pruebas). |
| `VITE_CLERK_PUBLISHABLE_KEY` | Frontend | Clave publicable de Clerk (es pública). |
| `VITE_API_URL` | Frontend | URL del backend en Vercel, sin `/` final. |

`GEMINI_URL`, `AI_TIMEOUT_SECONDS`, `MAX_CARACTERES` y `CLERK_JWKS_URL` usan su valor por defecto.

#### Pasos para desplegar

1. *Add New → Project*, importar `N13T4C0/ProyectoWebIA` y elegir como *Root Directory* `app2-Musicfy/backend` (Vercel detecta FastAPI). Añadir las variables del backend y desplegar. Comprobar que `/health` responde `{"status":"ok"}`.
2. Repetir con *Root Directory* `app2-Musicfy/frontend` (Vercel detecta Vite), con las variables del frontend.
3. Si la URL del frontend cambia, actualizar `ALLOWED_ORIGINS` en el backend y volver a desplegarlo (*Redeploy*).

**Problema encontrado:** el `vercel.json` del backend que generó la IA redirigía todas las rutas a `/api/index`, y con el preset de FastAPI la aplicación respondía 404 en todas las rutas. Se quitó la redirección (commit `8a153a2`).

#### Comprobaciones

| Fecha | Caso | Cómo | Resultado | Evidencia |
|---|---|---|---|---|
| 28/10/2026 | Válido | Con sesión de Clerk iniciada: géneros Pop y Electrónica. | 200: la pantalla muestra las recomendaciones. | `evidencias/app2-vercel-valido.png` |
| 28/10/2026 | Error | `POST /api/recommend` directo al backend, sin cabecera `Authorization`. | 401 `NO_AUTORIZADO` sin consultar a la IA. | `evidencias/app2-vercel-error.png` |

### AWS EC2

Pendiente: Docker, HTTPS, puertos y reinicio de contenedores (a cargo de Mario Luna Lopez).
