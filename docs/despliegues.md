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

**URL:** https://32-200-106-42.sslip.io/ (frontend y backend unificados mediante reverse proxy)

**Responsable:** Mario Luna Lopez

#### Entorno e Infraestructura en AWS Academy Learner Lab

El despliegue se realiza sobre la plataforma educativa **AWS Academy Learner Lab**, con los siguientes parámetros técnicos y de seguridad:

| Parámetro | Valor | Justificación / Observaciones |
|---|---|---|
| **Región** | `us-east-1` (N. Virginia) | Región autorizada por defecto en el Learner Lab. |
| **Instancia** | `t2.small` (1 vCPU, 2 GiB RAM) | Capacidad autorizada en AWS Academy Learner Lab. Dispone de 2 GiB de memoria RAM nativa (con 2 GiB de swap configurados como salvaguarda) para compilar y ejecutar el frontend y backend en Docker con total fluidez. |
| **Sistema Operativo** | Ubuntu Server 24.04 LTS (x86_64) | Imagen oficial de Canonical (`ami` de Ubuntu). |
| **Perfil IAM** | `LabInstanceProfile` | Rol preconfigurado de AWS Academy para instancias EC2. |
| **Almacenamiento** | 16 GiB gp3 | Volumen raíz EBS de la instancia. |

**Reglas del Grupo de Seguridad (`musicfy-sg` / `fp-analytics-sg`):**
- **Puerto 22 (SSH):** TCP entrante limitado a la IP del desarrollador (`Mi IP`) para administración remota segura.
- **Puerto 80 (HTTP):** TCP entrante abierto (`0.0.0.0/0`), imprescindible para resolver el reto HTTP-01 de Let's Encrypt (ACME) y redirigir todo el tráfico a HTTPS.
- **Puerto 443 (HTTPS):** TCP entrante abierto (`0.0.0.0/0`) para el servicio web seguro de producción.
- **Puerto 8000 (FastAPI):** No se expone al exterior; permanece aislado en la red interna de Docker Compose.

> [!NOTE] Limitación de AWS Academy Learner Lab y asignación de IP
> En AWS Academy Learner Lab las **IPs elásticas fijas (Elastic IP) no están permitidas** (la política IAM arroja `UnauthorizedOperation` ante la llamada a `AllocateAddress`). Además, cada sesión del laboratorio tiene una duración máxima de **4 horas**.
> Al cerrarse la sesión o detenerse la instancia, AWS reasigna una **nueva IPv4 pública dinámica** al reanudar. Esto es una restricción intrínseca del entorno educativo y no un fallo de la aplicación. Gracias al uso de `sslip.io` y Caddy, la aplicación se adapta a este cambio en menos de un minuto sin coste adicional.

#### Arquitectura del Despliegue

Despliegue multi-contenedor orquestado con `docker-compose.yml`:

| Servicio | Imagen / Dockerfile | Rol |
|---|---|---|
| `api` | `app2-Musicfy/backend/Dockerfile` (`python:3.12-slim`) | Backend FastAPI con Uvicorn en el puerto interno `8000`. |
| `web` | `app2-Musicfy/frontend/Dockerfile` (multietapa: `node:22` + `caddy:2`) | Servidor Caddy 2: compila y sirve la SPA de Vue 3, reverse proxy de `/api/*` y `/health` hacia `api:8000`, y terminación TLS automática. |

- **Terminación TLS y HTTPS automático:** Caddy gestiona de manera desatendida la solicitud, emisión y renovación del certificado TLS de Let's Encrypt para el dominio dinámico `32-200-106-42.sslip.io`. Los certificados se conservan en el volumen Docker persistente `caddy_data`.

#### Ubicación y Gestión de Secretos

Los secretos **nunca viajan en el repositorio ni en las imágenes Docker**:
- En el servidor EC2 residen exclusivamente en `/home/ubuntu/ProyectoWebIA/app2-Musicfy/backend/.env`.
- Los archivos `.env` están excluidos por `.gitignore` y ambos `.dockerignore`.
- En el frontend solo se inyecta la clave publicable `VITE_CLERK_PUBLISHABLE_KEY`.

| Variable | Archivo | Uso |
|---|---|---|
| `DOMINIO` | `app2-Musicfy/.env` | Dominio público para Caddy (`32-200-106-42.sslip.io`). |
| `VITE_CLERK_PUBLISHABLE_KEY` | `app2-Musicfy/.env` | Clave publicable de Clerk para compilar el frontend. |
| `VITE_API_URL` | `app2-Musicfy/.env` | Vacía (misma procedencia a través del proxy inverso de Caddy). |
| `GEMINI_API_KEY` | `app2-Musicfy/backend/.env` | Clave de la API de Gemini (secreta). |
| `GEMINI_URL` | `app2-Musicfy/backend/.env` | Endpoint compatible con OpenAI. |
| `GEMINI_MODEL` | `app2-Musicfy/backend/.env` | Modelo de IA (`gemini-3.5-flash-lite`). |
| `MAX_TOKENS` | `app2-Musicfy/backend/.env` | Límite de tokens de respuesta (600). |
| `MAX_CARACTERES` | `app2-Musicfy/backend/.env` | Longitud máxima de `tastes` (500). |
| `AI_TIMEOUT_SECONDS` | `app2-Musicfy/backend/.env` | Tiempo máximo de espera a la IA (25 s). |
| `CLERK_ISSUER` | `app2-Musicfy/backend/.env` | Emisor de Clerk (`https://ultimate-mullet-5413.clerk.accounts.dev`). |
| `ALLOWED_ORIGINS` | `app2-Musicfy/backend/.env` | Origen permitido para CORS y claim `azp` (`https://32-200-106-42.sslip.io`). |

#### Pasos para el Primer Despliegue

1. **Lanzar la instancia:** En la consola de AWS Academy Learner Lab (`us-east-1`), lanzar Ubuntu 24.04 LTS (`t2.small`, nombre `musicfy-app2`) con `LabInstanceProfile`.
2. **Grupo de seguridad:** Abrir TCP 22 (SSH desde Mi IP), TCP 80 (HTTP) y TCP 443 (HTTPS).
3. **Memoria swap y Docker:** Conectar por SSH y ejecutar:
   ```bash
   sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```
   Instalar Docker Engine y `docker-compose-plugin` (guía G17).
4. **Subir el proyecto y configurar `.env`:** Transferir el proyecto mediante `scp` o Git a `~/ProyectoWebIA/app2-Musicfy` y crear los ficheros `.env` y `backend/.env` con los valores reales.
5. **Construcción y arranque:** Ejecutar `docker compose up -d --build`.
6. **Comprobación de salud:** Verificar con `curl https://32-200-106-42.sslip.io/health` que devuelve `{"status":"ok"}`.

#### Procedimiento Reproducible para Relanzar tras Caducar la Sesión (Nueva IP)

Cuando la sesión de 4 horas del Learner Lab caduca o la máquina se reinicia, se ejecuta este procedimiento (menos de 1 minuto):

1. En AWS Academy pulsar **Start Lab** y anotar la **nueva IPv4 pública** asignada a la instancia EC2 (ejemplo: `54.210.88.99`).
2. Conectar por SSH a la nueva IP.
3. Actualizar la IP en los archivos `.env`:
   ```bash
   cd ~/ProyectoWebIA/app2-Musicfy
   sed -i 's/DOMINIO=.*/DOMINIO=54-210-88-99.sslip.io/' .env
   sed -i 's|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://54-210-88-99.sslip.io|' backend/.env
   ```
4. Si procede, añadir `https://54-210-88-99.sslip.io` a los orígenes autorizados en el panel de Clerk.
5. Levantar de nuevo los contenedores:
   ```bash
   sudo docker compose up -d
   ```
   *(No hace falta `--build` ya que las imágenes están compiladas. Caddy solicitará automáticamente el nuevo certificado TLS para el nuevo subdominio en pocos segundos).*

#### Comprobaciones

| Fecha | Caso | Cómo | Resultado | Evidencia |
|---|---|---|---|---|
| 28/10/2026 | Válido | Con sesión de Clerk activa desde navegador móvil vía HTTPS: géneros Indie y Rock, texto «música para concentrarse». | 200: la pantalla muestra las recomendaciones correctamente con candado SSL válido emitido por Let's Encrypt. | `evidencias/app2-ec2-valido.png` |
| 28/10/2026 | Error | `POST https://32-200-106-42.sslip.io/api/recommend` mediante `curl` sin cabecera `Authorization`. | 401 `NO_AUTORIZADO`: rechazo inmediato antes de validar datos o llamar a la IA. | `evidencias/app2-ec2-error.png` |
| 28/10/2026 | Reinicio (PR-15) | Petición con recomendación visible, reinicio con `docker compose down && docker compose up -d` y recarga del navegador. | La aplicación arranca sin datos previos ni almacenamiento de sesiones; el único volumen retenido es `caddy_data` (certificados TLS). | Verificado en logs y terminal |