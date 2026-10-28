# Uso de inteligencia artificial en Musicfy

Este documento recoge dos cosas distintas:

1. **La IA que usa la aplicación** para generar las recomendaciones.
2. **La IA que ha usado el equipo** como ayuda durante el desarrollo, como pide el enunciado.

## 1. IA de la aplicación

### Proveedor y configuración

| Parámetro | Valor | Dónde se configura |
|---|---|---|
| Proveedor | API de Gemini de Google (Google AI Studio), punto de acceso compatible con OpenAI | `GEMINI_URL` |
| Modelo | `gemini-3.5-flash-lite` | `GEMINI_MODEL` |
| Clave | Clave de Google AI Studio, solo en la configuración privada del backend | `GEMINI_API_KEY` en `backend/.env` y en las variables de entorno de Vercel |
| Máximo de tokens de respuesta | 600 | `MAX_TOKENS` |
| Tiempo máximo de espera | 25 segundos | `AI_TIMEOUT_SECONDS` |
| Temperatura | 0,7 | `backend/ai_client.py` |
| Consultas por envío | Una sola | Diseño del backend (RF-03) |

La clave de la API de Gemini solo está en `backend/.env`, que no se sube al repositorio. En el repositorio solo está `backend/.env.example`, con valores ficticios.

### Instrucciones que recibe el modelo (resumen del prompt del sistema)

El backend envía al modelo unas instrucciones fijas y, a continuación, el texto `tastes` del usuario. Las instrucciones piden:

- Actuar como el recomendador musical de Musicfy.
- Recomendar entre 3 y 5 artistas o bandas afines a lo que describe el usuario.
- Para cada uno: el nombre, por qué encaja y una canción o álbum para empezar.
- Responder en español, en texto plano y sin HTML.

El texto completo está en `SYSTEM_PROMPT`, dentro de `backend/ai_client.py`. El número y el formato de las recomendaciones son una instrucción al modelo, no algo que el backend garantice (SUP-01 en la ERS).

### Historial de modelos

| Fecha | Proveedor | Modelo | Motivo del cambio | Comprobación |
|---|---|---|---|---|
| Octubre de 2026 | OpenRouter | `meta-llama/llama-3.3-70b-instruct` | Valor inicial por defecto en `config.py` y `.env.example`. | — |
| Octubre de 2026 | OpenRouter | `google/gemini-2.5-flash` | Modelo usado por el equipo en su `.env`. | PR-13 del 13/10/2026. |
| 19/10/2026 | API de Gemini de Google | `gemini-3.5-flash-lite` | El saldo y el límite de peticiones de OpenRouter se agotaban muy rápido; el plan gratuito de Gemini permite seguir haciendo pruebas y demostraciones. | PR-13 del 19/10/2026 en el despliegue de Vercel. |

Se mantiene una única API de IA en todo momento, como exige el enunciado: el cambio sustituye un proveedor por otro.

La App 2 usa el mismo proveedor, modelo y límites que la App 1. En el plan de Spec Kit, la IA propuso `gemini-2.5-flash` con `MAX_TOKENS=800`; el 27/10/2026 el equipo lo cambió por `gemini-3.5-flash-lite` con 600, porque ese modelo ya estaba probado en el despliegue de App 1, la comparativa es más justa y se evita que el razonamiento de `gemini-2.5-flash` consuma los tokens y deje respuestas vacías.

### Incidencias

| Fecha | Problema | Causa | Solución |
|---|---|---|---|
| 13/10/2026 | La petición válida devolvía 502. | OpenRouter respondía 402: sin un máximo de tokens, reservaba saldo para la respuesta más larga posible del modelo y la cuenta no tenía suficiente. | Se añadió `MAX_TOKENS` (600) a la petición. |
| 19/10/2026 | Las peticiones a la IA fallaban en el despliegue de Vercel. | El saldo y el límite de peticiones de OpenRouter se agotaban: la app respondía que no quedaban más solicitudes disponibles. | Cambio a la API de Gemini de Google. Resuelto el 19/10/2026. |

## 2. IA usada por el equipo durante el desarrollo

El enunciado pide registrar qué herramientas de IA se han usado, para qué, qué se aceptó o rechazó y cómo se comprobó. Cada integrante añade aquí sus propios usos.

| Fecha | Integrante | Herramienta | Finalidad | Qué se aceptó o rechazó | Comprobación humana |
|---|---|---|---|---|---|
| 12-13/10/2026 | David | Claude (chat) | Aprender a escribir pruebas con pytest y mocks. | Se aceptó la estructura de los tests; se escribieron a mano, lección a lección. | Ejecución de pytest y rotura intencionada de tests para entender cada comprobación. |
| 13/10/2026 | David | Claude (chat) | Diagnosticar el error 502 al llamar a OpenRouter. | Se aceptó limitar `max_tokens`. | Script de diagnóstico y prueba real en `/docs`. |
| 15/10/2026 | David | Claude (chat) | Borrador de la ERS a partir del código y de las pruebas. | Se adaptaron RF-01, DAT-01, IU-01 y RNF-04 al formulario real; se corrigió el ancho de RNF-04 a 320 px. | Revisión del equipo y comprobaciones con F12 en el navegador. |
| 19/10/2026 | David | Claude (chat) | Diagramas de casos de uso y de actividad en Mermaid. | Se aceptaron ambos diagramas. | Revisión de que coinciden con el comportamiento real de la app. |
| 25/10/2026 | David | Claude (chat) | Borrador de la ERS de App 2 a partir de la ERS de App 1. | Se aceptó la estructura; se añadieron RF-06, RNF-05 y el flujo de acceso no autorizado. | Revisión contra el enunciado y la plantilla. |
| 25/10/2026 | Jose Antonio | Spec Kit 1.2.4.dev0 con Claude Code | Constitución, especificación, plan técnico y tareas de App 2. | Se aceptaron tras revisarlos: sin funciones fuera de alcance. La verificación con PyJWT y JWKS, propuesta por la IA, queda pendiente de revisión por Mario. | Revisión contra la ERS de App 2 (15 min). |
| 26/10/2026 | David | Claude (chat) | Revisar `spec.md` y `tasks.md` contra la ERS de App 2. | Se detectó que el plan usaba otro modelo y otro límite de tokens que la App 1. | Comparación manual de los documentos; ERS de App 2 actualizada a la versión 0.2. |
| 27/10/2026 | Jose Antonio | Claude Code (`/speckit-implement`) | Implementar las tareas T001 a T039: backend, frontend, Clerk, Docker y 59 pruebas. | Se aceptaron las desviaciones `<Show>` de Clerk, `node:22` y Python 3.14. Se rechazó el modelo propuesto. Se corrigió el arranque local, porque el código generado no cargaba `.env`. | Revisión de cada fase, 59 pruebas en verde y prueba manual en local con Clerk y Gemini reales (T040). |
