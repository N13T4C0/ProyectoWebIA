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

## App 2

Pendiente: Vercel y AWS EC2 con Docker y HTTPS (sección a cargo de Mario Luna Lopez).
