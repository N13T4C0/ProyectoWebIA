# Proceso de desarrollo de Musicfy

Este documento recoge cómo se ha trabajado: el reparto de tareas, el tiempo dedicado y las decisiones y problemas a medida que ocurren. Sirve de base para `docs/comparativa.md` y para la presentación.

Cada integrante añade sus propias entradas. Las que se reconstruyen después del momento en que ocurrieron se marcan como **reconstruido**, con la fecha aproximada.

## 1. Equipo y reparto

| Integrante | App 1 | App 2 |
|---|---|---|
| Mario Luna Lopez | Backend: FastAPI, validación de la entrada con Pydantic, conexión con la IA (OpenRouter y después Gemini), tratamiento de errores (422, 502, 504)  | Despliegues: aplicación de Clerk, App 2 en Vercel y en AWS EC2 con HTTPS; documentación en `despliegues.md`. Revisión del plan técnico de Spec Kit. |
| Jose Antonio Nieto Perez | Frontend: SPA en Vue.js con Tailwind CSS, formulario con botones de género y texto libre, estados de espera, resultado y error, y y despliegue en Vercel. | Desarrollo de la App 2 con Spec Kit: constitución, especificación, plan, tareas e implementación con el agente de IA, incluida la integración de Clerk en la misma pantalla. |
| David Molina Castillo | Pruebas con pytest y mocks, capa de IA, ERS y presentación | Pruebas, ERS de App 2, Docker en local, documentación (`uso-ia.md`, `comparativa.md`) y presentación |

## 2. Registro de tiempos

Una fila por tarea. El tiempo es el dedicado por esa persona a esa tarea. En App 2 se incluye el tiempo de revisar y corregir lo que propone la IA.

**Fase:** Análisis, Backend, Frontend, Pruebas, Revisión IA, Clerk, Despliegue, Docker, AWS, Documentación o Presentación.

### App 1

| Fecha | Integrante | Fase | Tarea | Tiempo | Observaciones |
|---|---|---|---|---|---|
| 11/10/2026 | David | Pruebas | Plan de casos de prueba (`docs/pruebas.md`) | Pendiente | Reconstruido |
| 12-13/10/2026 | David | Pruebas | Tests con pytest y mocks (12 tests) | Pendiente | Reconstruido |
| 13/10/2026 | David | Backend | Diagnóstico del error 402 y límite de `MAX_TOKENS` | Pendiente | Reconstruido |
| 15/10/2026 | David | Análisis | ERS de App 1 (versiones 0.1 y 0.2) y pruebas manuales PR-14 a PR-17 | Pendiente | Reconstruido |
| 19/10/2026 | David | Análisis | ERS versiones 0.3 y 0.4, diagramas y `uso-ia.md` | Pendiente | Reconstruido |
| 25/10/2026 | Equipo | Análisis | Revisión cruzada y ERS versión 1.0 | Pendiente | |
| Pendiente | Pendiente | Backend | Pendiente | Pendiente | |
| Pendiente | Pendiente | Frontend | Pendiente | Pendiente | |
| Pendiente | Pendiente | Despliegue | Despliegue en Vercel | Pendiente | |

### App 2

| Fecha | Integrante | Fase | Tarea | Tiempo | Observaciones |
|---|---|---|---|---|---|
| 25/10/2026 | David | Análisis | Borrador de `docs/ERS-app2.md` | Pendiente | |
| Pendiente | Pendiente | Análisis | Constitución y especificación con Spec Kit | Pendiente | |
| Pendiente | Pendiente | Revisión IA | Revisión de la especificación y el plan | Pendiente | |

## 3. Decisiones

| Fecha | Decisión | Motivo | Quién la tomó |
|---|---|---|---|
| 11/10/2026 | La aplicación se llama Musicfy. | Elección del equipo. | Equipo |
| 11/10/2026 | Repositorio estructurado en carpetas `frontend` y `backend`. | Separar las dos capas desde el principio. | Equipo |
| Octubre de 2026 | Frontend con Vue.js y Tailwind CSS. | Pendiente | Equipo |
| 12/10/2026 | Proyecto reorganizado dentro de `app1-Musicfy`. | Separar la App 1 de la App 2, según la estructura recomendada. | Pendiente |
| 13/10/2026 | Las pruebas simulan la función `ask_model` en lugar de la API real. | No gastar créditos, poder provocar fallos y obtener resultados repetibles. | David |
| 13/10/2026 | Límite de 600 tokens de respuesta (`MAX_TOKENS`). | Evitar el error 402 por reserva de saldo y controlar el gasto. | Equipo |
| 15/10/2026 | El formulario combina botones de género y texto libre en un único campo `tastes`. | Facilitar la descripción sin cambiar el contrato del backend. | Pendiente |
| 19/10/2026 | Cambio de proveedor de IA: de OpenRouter a la API de Gemini de Google. | Pendiente: motivo concreto. | Pendiente |
| 19/10/2026 | Frontend y backend desplegados en Vercel. | Despliegue obligatorio de App 1. Pendiente: uno o dos proyectos y por qué. | Pendiente |
| 25/10/2026 | En App 2, un integrante lleva Spec Kit; los otros dos revisan la especificación y el plan antes del commit. | Pendiente | Equipo |
| 25/10/2026 | Rotación de roles: Docker en local lo hace el responsable de pruebas y EC2 el responsable de backend. | Que todos comprendan el flujo completo, como pide el enunciado. | Equipo |

## 4. Problemas encontrados

| Fecha | Problema | Causa | Solución | Quién lo resolvió |
|---|---|---|---|---|
| 13/10/2026 | Al ejecutar pytest aparece un aviso de deprecación de Starlette sobre `httpx`. | Cambio previsto en la librería de pruebas de FastAPI. | No afecta a los resultados; anotado en `docs/pruebas.md`. | David Molina Castillo |
| 13/10/2026 | La petición válida devolvía 502. | OpenRouter respondía 402 por la reserva de saldo para la respuesta máxima. | Añadir `MAX_TOKENS` (600). | Mario Luna Lopez |
| 19/10/2026 | Las peticiones a la IA fallaban en el despliegue de Vercel. | La API de OpenRouter seguía dando problemas por que expiraban el saldo de peticiones muy rápidamente | Se cambió a otra modelo de API (Gemini) | Mario Luna Lopez |
