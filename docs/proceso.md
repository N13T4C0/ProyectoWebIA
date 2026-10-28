# Proceso de desarrollo de Musicfy

Este documento recoge cómo se ha trabajado: el reparto de tareas, el tiempo dedicado y las decisiones y problemas a medida que ocurren. Sirve de base para `docs/comparativa.md` y para la presentación.

Cada integrante añade sus propias entradas. Las que se reconstruyen después del momento en que ocurrieron se marcan como **reconstruido**, con la fecha aproximada.

## 1. Equipo y reparto

| Integrante | App 1 | App 2 |
|---|---|---|
| Mario Luna Lopez | Backend: FastAPI, validación de la entrada con Pydantic, conexión con la IA (OpenRouter y después Gemini), tratamiento de errores (422, 502, 504)  | Despliegues: aplicación de Clerk, App 2 en Vercel y en AWS EC2 con HTTPS; documentación en `despliegues.md`. Revisión del plan técnico de Spec Kit. |
| Jose Antonio Nieto Perez | Frontend: SPA en Vue.js con Tailwind CSS, formulario con botones de género y texto libre, estados de espera, resultado y error, y y despliegue en Vercel. | Desarrollo de la App 2 con Spec Kit: constitución, especificación, plan, tareas e implementación con el agente de IA, incluida la integración de Clerk en la misma pantalla. |
| David Molina Castillo | Pruebas con pytest y mocks, capa de IA, ERS y presentación |Pruebas, ERS de App 2, documentación (`uso-ia.md`, `comparativa.md`) y presentación|

## 2. Registro de tiempos

Una fila por tarea. El tiempo es el dedicado por esa persona a esa tarea. En App 2 se incluye el tiempo de revisar y corregir lo que propone la IA.

**Fase:** Análisis, Backend, Frontend, Pruebas, Revisión IA, Clerk, Despliegue, Docker, AWS, Documentación o Presentación.

### App 1

| Fecha | Integrante | Fase | Tarea | Tiempo | Observaciones |
|---|---|---|---|---|---|
| 11/10/2026 | David Molina | Pruebas | Plan de casos de prueba (`docs/pruebas.md`) | 1 h | Reconstruido. Estimación. Casos sacados de los límites acordados (500 caracteres, 25 s) y de los códigos de error. |
| 12-13/10/2026 | David Molina | Pruebas | Tests con pytest y mocks (12 tests) | 4 h | Reconstruido. Estimación. Incluye aprender pytest y los mocks de `ask_model` y romper tests a propósito para entender cada comprobación. |
| 13/10/2026 | David Molina | Backend | Diagnóstico del error 402 y límite de `MAX_TOKENS` | 1,5 h | Reconstruido. Estimación. Script de diagnóstico para ver el código real de OpenRouter. |
| 15/10/2026 | David Molina | Análisis | ERS de App 1 (versiones 0.1 y 0.2) y pruebas manuales PR-14 a PR-17 | 4 h | Reconstruido. Estimación. Pruebas manuales con F12 en el navegador. |
| 19/10/2026 | David Molina | Análisis | ERS versiones 0.3 y 0.4, diagramas y `uso-ia.md` | 3 h | Reconstruido. Estimación. Diagramas de casos de uso, actividad y secuencia en Mermaid. |
| 25/10/2026 | Equipo | Análisis | Revisión cruzada y ERS versión 1.0 | 1,5 h | |
| 11-19/10/2026 | Mario Luna | Backend | Desarrollo de la API en FastAPI: schemas Pydantic, cliente Gemini y gestión de errores (422, 502, 504) | 4 h | Reconstruido. Estimación. Incluye la integración inicial con OpenRouter y la posterior migración a la API de Gemini. |
| 11/10/2026 | Jose Antonio Nieto | Análisis | Estructura inicial del repositorio, `.gitignore`, `.env` y configuración inicial del backend | 0,5 h | Estimación |
| 11/10/2026 | Jose Antonio Nieto | Frontend | Proyecto Vue + Vite con Tailwind y cliente de la API con mock y gestión de errores | 1,5 h | Estimación |
| 11/10/2026 | Jose Antonio Nieto | Frontend | Pantalla única de estilo CRT: título WebGL, logo animado, animación de encendido y diseño | 3 h | Estimación |
| 13/10/2026 | Jose Antonio Nieto | Frontend | Selector de géneros con botones (máximo 5) y resaltado de los artistas recomendados | 2 h | Estimación |
| 13/10/2026 | Jose Antonio Nieto | Backend | Prompt con formato fijo y reglas de calidad para las recomendaciones | 0,5 h | Estimación |
| 14/10/2026 | Jose Antonio Nieto | Frontend | Ajustes de diseño: portada compacta sin scroll y sin barra durante la animación | 1 h | Estimación |
| 15/10/2026 | Jose Antonio Nieto | Despliegue | Despliegue en Vercel (`vercel.json`, ruta relativa `/api` en producción) | 1,5 h | Estimación |
| 19/10/2026 | Jose Antonio Nieto | Despliegue | Variables de entorno de Vercel y portal de prácticas con enlace a la demo | 2 h | Estimación |

### App 2

| Fecha | Integrante | Fase | Tarea | Tiempo | Observaciones |
|---|---|---|---|---|---|
| 25/10/2026 | David Molina | Análisis | Borrador de `docs/ERS-app2.md` (versión 0.1) | 1.5 h | Estimación. A partir de la ERS de App 1, con RF-06, RNF-05 y el flujo de acceso no autorizado. |
| 26/10/2026 | David Molina | Revisión IA | Revisión de `spec.md` y `tasks.md` contra la ERS de App 2 (versión 0.2) |  30 min | Estimación. Detecta que el plan usa otro modelo y otro límite de tokens que la App 1. Se mueve `docs/` a la raíz del repositorio. |
| 27-28/10/2026 | David Molina | Documentación | Datos de App 2 en `uso-ia.md` y `comparativa.md`, ERS de App 2 versión 0.3 | 1 h | Estimación. |
| 25/10/2026 | Jose Antonio Nieto | Análisis | Inicializar `app2-Musicfy` con Spec Kit e instalar Claude Code | 10 min | Spec Kit 1.2.4.dev0, integración con Claude Code y scripts de PowerShell. |
| 25/10/2026 | Jose Antonio Nieto | Análisis | Constitución (`/speckit-constitution`) | 5 min | Seis principios a partir de la ERS. Deja PEN-02 y PEN-04 como pendientes. |
| 25/10/2026 | Jose Antonio Nieto | Análisis | Especificación (`/speckit-specify`) | 5 min | La IA tardó 1 min 22 s. 4 historias de usuario y 29 requisitos trazados a la ERS. No hizo falta `/speckit-clarify`. |
| 25/10/2026 | Jose Antonio Nieto | Análisis | Plan técnico (`/speckit-plan`) | 6 min | La IA tardó 1 min 58 s. Plan, investigación técnica, modelo de datos, contratos y quickstart. Resuelve PEN-02. |
| 25/10/2026 | Jose Antonio Nieto | Análisis | Tareas (`/speckit-tasks`) | 5 min | La IA tardó 2 min 29 s. 41 tareas en 7 fases. |
| 25/10/2026 | Jose Antonio Nieto | Revisión IA | Revisión de la constitución, la especificación, el plan y las tareas | 15 min | Comprobado contra la ERS de App 2. Sin funciones fuera de alcance. |
| 27/10/2026 | Jose Antonio Nieto | Revisión IA | Fases 1 y 2 (`/speckit-implement`, T001–T015): preparación y base común | 15 min | La IA tardó 4 min 20 s. Usó Python 3.14 en local en vez del 3.12 del plan. |
| 27/10/2026 | Jose Antonio Nieto | Revisión IA | Fase 3 (US1, T016–T020): recomendaciones con sesión | 5 min | La IA tardó 1 min 26 s. |
| 27/10/2026 | Jose Antonio Nieto | Revisión IA | Fase 4 (US2, T021–T025): acceso con Clerk y 401 | 5 min | La IA tardó 1 min 43 s. Usó `<Show>` porque `@clerk/vue` 2.x ya no tiene `<SignedIn>`/`<SignedOut>`. Añadió por su cuenta descartar la respuesta si se cierra sesión durante la espera. |
| 27/10/2026 | Jose Antonio Nieto | Revisión IA | Fases 5 y 6 (US3 y US4, T026–T032): validación y errores de la IA | 5 min | La IA tardó 1 min 40 s. 59 pruebas automáticas en verde (App 1: 12). |
| 27/10/2026 | Jose Antonio Nieto | Revisión IA | Fase 7 (T033–T039): Docker, accesibilidad y revisión de seguridad | 10 min | Dockerfile del frontend cambiado de `node:20` a `node:22` (Node 20 sin soporte). |
| 27/10/2026 | Jose Antonio Nieto | Pruebas | Prueba manual en local con sesión real de Clerk y Gemini (T040: PR-13, PR-16, PR-17, PR-21) | 20 min | Incluye el diagnóstico del error de CORS por no cargar `.env`. |
| 28/10/2026 | Jose Antonio Nieto | Despliegue | Despliegue de la App 2 en Vercel (dos proyectos), corrección de `vercel.json` y comprobaciones PR-22 | 30 min | Primero lo iba a hacer Mario; con el plan Hobby y el repositorio privado solo despliega el propietario, así que lo hizo Jose. |
| 26/10/2026 | Mario Luna | Revisión IA | Revisión del plan técnico (`plan.md`) y contratos de la API | 30 min | Comprobado el orden de validación (401 antes de 422), contrato de errores y arquitectura de despliegue con Caddy. |
| 28/10/2026 | Mario Luna | Despliegue | Despliegue de la App 2 en AWS EC2 con Docker Compose y Caddy (HTTPS) | 2 h | Preparación de la instancia en AWS Academy Learner Lab, swap, puertos 22/80/443, Docker Compose, Caddy con certificado Let's Encrypt y pruebas PR-14, PR-15 y PR-23. |

## 3. Decisiones

| Fecha | Decisión | Motivo | Quién la tomó |
|---|---|---|---|
| 11/10/2026 | La aplicación se llama Musicfy. | Elección del equipo. | Equipo |
| 11/10/2026 | Repositorio estructurado en carpetas `frontend` y `backend`. | Separar las dos capas desde el principio. | Equipo |
| Octubre de 2026 | Frontend con Vue.js y Tailwind CSS. | Vue.js permite montar una SPA de una sola pantalla con poco código y es fácil de aprender; Tailwind CSS da un diseño cuidado y adaptable a móvil sin escribir hojas de estilo propias. | Jose Antonio Nieto |
| 12/10/2026 | Proyecto reorganizado dentro de `app1-Musicfy`. | Separar la App 1 de la App 2, según la estructura recomendada. | Jose Antonio Nieto |
| 13/10/2026 | Las pruebas simulan la función `ask_model` en lugar de la API real. | No gastar créditos, poder provocar fallos y obtener resultados repetibles. | David Molina|
| 13/10/2026 | Límite de 600 tokens de respuesta (`MAX_TOKENS`). | Evitar el error 402 por reserva de saldo y controlar el gasto. | Equipo |
| 15/10/2026 | El formulario combina botones de género y texto libre en un único campo `tastes`. | Facilitar la descripción sin cambiar el contrato del backend. | Jose Antonio Nieto |
| 19/10/2026 | Cambio de proveedor de IA: de OpenRouter a la API de Gemini de Google. | El saldo y el límite de peticiones de OpenRouter se agotaban muy rápido; el plan gratuito de Gemini permite seguir probando. | Mario Luna Lopez |
| 19/10/2026 | Frontend y backend desplegados en Vercel. | Despliegue obligatorio de App 1. Un único proyecto de Vercel con dos servicios (frontend y backend) y una regla que envía `/api` al backend: una sola URL y sin necesidad de CORS. | Jose Antonio Nieto |
| 25/10/2026 | En App 2, un integrante lleva Spec Kit; los otros dos revisan la especificación y el plan antes del commit. | Encaja con el reparto de App 2: Mario lleva Clerk y los despliegues, y David las pruebas y la documentación, así que el desarrollo con Spec Kit queda a Jose. La revisión de los otros dos evita que la especificación dependa del criterio de una sola persona. | Equipo |
| 25/10/2026 | Rotación de roles: Docker en local lo hace el responsable de pruebas y EC2 el responsable de backend. | Que todos comprendan el flujo completo, como pide el enunciado. | Equipo |
| 25/10/2026 | La App 2 va en la carpeta `app2-Musicfy`, creada vacía con `specify init`. | Separarla de la App 1 y cumplir RES-09: un proyecto nuevo sin copiar código. | Jose Antonio Nieto |
| 25/10/2026 | Spec Kit con Claude Code como agente de IA. | Spec Kit tiene integración oficial con Claude Code (comandos `/speckit-*`), funciona en la terminal de VS Code en Windows y el equipo ya disponía de una cuenta de Claude. | Jose Antonio Nieto |
| 25/10/2026 | La App 2 ofrece los mismos 12 géneros que la App 1. | La ERS no fija la lista, y así se pueden comparar las dos apps. | Jose Antonio Nieto |
| 25/10/2026 | El token de Clerk se verifica con PyJWT y JWKS, no con el SDK. | Aprobado por Mario Luna tras revisar el plan: evita almacenar la clave secreta de Clerk en el backend cumpliendo el principio de menor privilegio (solo URLs públicas). | IA / Jose Antonio Nieto / Mario Luna |
| 27/10/2026 | La App 2 usa el mismo modelo y límite que la App 1 (`gemini-3.5-flash-lite` y `MAX_TOKENS=600`), en lugar de `gemini-2.5-flash` y 800 que propuso la IA en el plan. | El modelo ya está probado en el despliegue de App 1, la comparativa es más justa y se evita que el razonamiento de `gemini-2.5-flash` consuma los tokens y deje respuestas vacías. | Jose Antonio Nieto |
| 27/10/2026 | Se aceptan las desviaciones de la IA respecto a `tasks.md`: `<Show>` de Clerk en lugar de `<SignedIn>`/`<SignedOut>` y `node:22` en lugar de `node:20`. | El plan se había quedado desfasado respecto a las versiones reales de las librerías; las desviaciones quedan anotadas en `tasks.md`. | Jose Antonio Nieto |
| 27/10/2026 | La App 2 se desarrolla y prueba en local con Python 3.14 y se despliega con Python 3.12, como fija el plan (`python:3.12-slim` en el `Dockerfile`). | Python 3.14 es la versión instalada en el equipo de desarrollo; no se instaló la 3.12 porque las 59 pruebas pasan igual y el código no usa nada propio de una versión. Desviación detectada y comunicada por la IA en la fase 1. | Jose Antonio Nieto |
| 28/10/2026 | Docker en local pasa de David Molina a Mario Luna Lopez, responsable del despliegue en EC2. | El despliegue en AWS EC2 requiere Docker, y los archivos de Docker ya los generó la IA con Spec Kit (fase 7, T033–T039). | Equipo |

## 4. Problemas encontrados

| Fecha | Problema | Causa | Solución | Quién lo resolvió |
|---|---|---|---|---|
| 13/10/2026 | Al ejecutar pytest aparece un aviso de deprecación de Starlette sobre `httpx`. | Cambio previsto en la librería de pruebas de FastAPI. | No afecta a los resultados; anotado en `docs/pruebas.md`. | David Molina Castillo |
| 13/10/2026 | La petición válida devolvía 502. | OpenRouter respondía 402 por la reserva de saldo para la respuesta máxima. | Añadir `MAX_TOKENS` (600). | Mario Luna Lopez |
| 19/10/2026 | Las peticiones a la IA fallaban en el despliegue de Vercel: la app respondía que no quedaban más solicitudes. | El saldo y el límite de peticiones de OpenRouter se agotaban muy rápido. | Cambio de proveedor a la API de Gemini de Google. | Mario Luna Lopez |
| 25/10/2026 | `git pull` descargaba los cambios pero no los aplicaba. | Había un cambio local sin commitear en `app1/backend/config.py`, archivo que en remoto se había movido a `app1-Musicfy`. | Guardar el cambio con `git stash` y aplicar los commits remotos. | Jose Antonio Nieto |
| 25/10/2026 | `claude` no se reconocía en PowerShell. | Claude Code no estaba instalado. | Instalarlo con el instalador oficial (`install.ps1`) y reabrir la terminal. | Jose Antonio Nieto |
| 27/10/2026 | En la prueba manual, el frontend mostraba «No se puede conectar con el servicio» y el backend respondía 400 a las peticiones `OPTIONS`. | El código generado por la IA no carga el `.env` en local, así que `ALLOWED_ORIGINS` quedaba vacío y CORS rechazaba todo. Las 59 pruebas automáticas no lo detectaban. | Arrancar con `uvicorn ... --env-file .env`; `quickstart.md` y `docs/pruebas.md` actualizados. | Jose Antonio Nieto |
| 28/10/2026 | En Vercel, el backend de la App 2 respondía 404 en todas las rutas, incluida `/health`. | El `vercel.json` generado por la IA redirigía todas las peticiones a `/api/index`; con el preset de FastAPI de Vercel la aplicación recibía esa ruta y no la encontraba. No se detectaba en local ni en las pruebas. | Quitar la redirección de `vercel.json` (commit `8a153a2`). | Jose Antonio Nieto |
| 28/10/2026 | En EC2, la construcción de la imagen de frontend consumía casi toda la memoria RAM de la instancia (1 GiB) con riesgo de Out Of Memory. | Las instancias `t3.micro` de AWS Academy disponen de memoria limitada para compilaciones pesadas de Node/Vite. | Configurar un archivo swap de 2 GiB en Ubuntu antes de ejecutar Docker Compose. | Mario Luna Lopez |
| 28/10/2026 | Error de conexión no segura (SSL) al acceder inicialmente mediante el dominio con puntos (`32.200.106.42.sslip.io`). | Caddy y Let's Encrypt emitieron el certificado para el subdominio con guiones fijado en `DOMINIO` (`32-200-106-42.sslip.io`) para evitar problemas con certificados multinivel. | Acceder a la URL con guiones coincidente con la directiva del Caddyfile. | Mario Luna Lopez |
