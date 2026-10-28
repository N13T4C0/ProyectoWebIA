# Comparativa App 1 y App 2

Este documento compara los dos procesos de desarrollo de Musicfy:

- **App 1:** construcción manual y progresiva por el equipo.
- **App 2:** proyecto nuevo desde cero, guiado por especificaciones con GitHub Spec Kit y un agente de IA, con autenticación Clerk.

Ambas resuelven la misma necesidad con el mismo contrato (`POST /api/recommend`). Para comparar el flujo base se usan los mismos escenarios de aceptación (sección 6). El esfuerzo de Clerk y de infraestructura se separa del resto al comparar tiempos.

Los datos proceden de `docs/proceso.md`, `docs/pruebas.md`, `docs/uso-ia.md` y del historial de Git. Las cifras que no se midieron en su momento se indican como **estimación**.

## 1. Tiempo

Tiempo aproximado por fase, sumando a los tres integrantes. En App 2 se incluye el tiempo de revisar y corregir lo que propone la IA.

| Fase | App 1 | App 2 |
|---|---|---|
| Análisis y requisitos (ERS / especificación de Spec Kit) | Pendiente (estimación) | 46 min: 31 min con Spec Kit (la IA tardó unos 6 min) y 15 min de revisión. Falta sumar la ERS de App 2. |
| Backend (FastAPI, validación, llamada a la IA, errores) | Pendiente (estimación), más 0,5 h del prompt | Lo genera la IA con `/speckit-implement` (incluido en la revisión). |
| Frontend (formulario, estados, Tailwind) | 7,5 h (estimación) | Lo genera la IA con `/speckit-implement` (incluido en la revisión). |
| Pruebas con pytest y mocks | Pendiente (estimación) | La IA genera las 59 pruebas automáticas. Prueba manual en local: 20 min. |
| Revisión y corrección de propuestas de la IA | No aplica: App 1 se construyó manualmente | 40 min revisando las 7 fases de la implementación (la IA tardó unos 11 min en generarla). |
| Documentación | Pendiente (estimación) | Pendiente |
| **Total del flujo base** | **Pendiente** | **Pendiente** |

**Esfuerzo separado (no se suma al flujo base):**

| Tarea | App 1 | App 2 |
|---|---|---|
| Autenticación con Clerk | No aplica | Integración generada por la IA (fase 4, 5 min de revisión). Pendiente: tiempo de configurar la aplicación de Clerk. |
| Despliegue en Vercel | 3,5 h (estimación) | Pendiente |
| Docker en local | No aplica | Archivos generados por la IA (fase 7). Pendiente: prueba en local. |
| AWS EC2 con HTTPS | No aplica | Pendiente |

**Conclusión sobre el tiempo:** Pendiente.

## 2. Calidad

| Aspecto | App 1 | App 2 |
|---|---|---|
| Legibilidad del código | Pendiente | Pendiente |
| Validaciones de la entrada | Validación en backend con Pydantic (vacío, solo espacios, más de 500 caracteres) y en el frontend (sin géneros ni texto no se envía). | Las mismas validaciones en backend (`test_validation.py`) y frontend (PR-16). Además, la sesión se comprueba antes que la entrada: sin token y con cuerpo inválido responde 401, no 422. |
| Contrato JSON | `{"tastes"}` → `{"resultado"}` o `{"error": {"codigo", "mensaje"}}`, estable desde el principio. | El mismo contrato, más la cabecera `Authorization: Bearer`. El código 401 y su mensaje quedaron fijados en `contracts/api.md` antes de programar. |
| Tratamiento de errores | 422, 502 (`IA_NO_DISPONIBLE`, `RESPUESTA_INVALIDA`), 504 (`TIMEOUT`) y 500 (`ERROR_INTERNO`), sin detalles internos. | Los mismos, más 401 `NO_AUTORIZADO`. Comprobado que el registro del servidor no contiene datos ni tokens (PR-21 en local). |
| Pruebas automáticas | 12 tests con pytest y mocks de la IA, todos en verde (13/10/2026). | 59 tests, todos en verde (27/10/2026). Incluyen el verificador real de Clerk con claves de prueba y el cliente de Gemini con respuestas simuladas. No detectaron el fallo de arranque sin `.env`, porque no prueban la configuración real. |
| Consistencia con la ERS | Trazabilidad completa en `docs/ERS.md` (versión 1.0). | Los 29 requisitos de `spec.md` y las pruebas están trazados a los ID de `docs/ERS-app2.md`. Las desviaciones de la IA están anotadas en `tasks.md`. |

**Conclusión sobre la calidad:** Pendiente.

## 3. Errores

Problemas concretos encontrados, su origen y su solución.

### App 1

| Fecha | Problema | Origen | Solución |
|---|---|---|---|
| 12/10/2026 | Entorno de Python duplicado y carpetas reorganizadas a mitad del trabajo (`app1-Musicfy`). | Falta de acuerdo inicial sobre la ubicación del entorno y la estructura. | Volver a clonar el repositorio y crear un único entorno en `backend/.venv`. |
| 13/10/2026 | La petición válida devolvía 502 «El servicio de IA ha respondido con un error». | OpenRouter respondía 402: sin `max_tokens`, reservaba saldo para la respuesta máxima del modelo y la cuenta no tenía suficiente. | Limitar `MAX_TOKENS` a 600. Diagnosticado con un script que mostraba el código real de OpenRouter. |
| 19/10/2026 | Las peticiones a la IA fallaban en el despliegue de Vercel: la app respondía que no quedaban más solicitudes. | El saldo y el límite de peticiones de OpenRouter se agotaban muy rápido. | Cambio de proveedor a la API de Gemini de Google (plan gratuito). |
| 19/10/2026 | Los commits de algunos integrantes aparecen bloqueados por Vercel en GitHub. | El proyecto de Vercel pertenece a un solo integrante y no admite despliegues de commits de otros autores. | No afecta a la app desplegada. Pendiente de decidir si se cambia la configuración. |

### App 2

| Fecha | Problema | Origen | Solución |
|---|---|---|---|
| 25/10/2026 | El plan proponía `gemini-2.5-flash` con 800 tokens, distinto de la App 1. | Propuesta de la IA en `/speckit-plan`. | Cambiado por el modelo y el límite de App 1 el 27/10/2026. |
| 27/10/2026 | `tasks.md` pedía los componentes `<SignedIn>` y `<SignedOut>` de Clerk, que ya no existen en `@clerk/vue` 2.x. | El plan se basaba en versiones antiguas de las librerías. | La IA usó `<Show>`; el equipo aceptó la desviación y la anotó en `tasks.md`. |
| 27/10/2026 | El Dockerfile del frontend usaba `node:20`, sin soporte. | El plan estaba desfasado. | Cambiado a `node:22`. |
| 27/10/2026 | Python 3.14 en local en lugar del 3.12 del plan. | Versión instalada en el equipo. | Las 59 pruebas pasan con Python 3.14. |
| 27/10/2026 | En local, el frontend mostraba «No se puede conectar con el servicio» y CORS rechazaba todas las peticiones (`OPTIONS` → 400). | El código generado por la IA no carga `.env`, así que `ALLOWED_ORIGINS` quedaba vacío. Las 59 pruebas no lo detectaron. | Arrancar con `--env-file .env`; `quickstart.md` actualizado. |

**Conclusión sobre los errores:** Pendiente.

## 4. Mantenibilidad

Qué cambio pequeño sería fácil o difícil en cada app y por qué. Son ejemplos para razonar; no se implementan como nuevas funciones.

| Cambio hipotético | App 1 | App 2 |
|---|---|---|
|  Cambiar el modelo o el proveedor de IA | Fácil en la práctica: se hizo de OpenRouter a Gemini cambiando `config.py`, `ai_client.py` y las variables de entorno; los tests no cambiaron porque simulan `ask_model`. | Fácil: el cambio de `gemini-2.5-flash` con 800 tokens al modelo de App 1 se hizo con las variables `GEMINI_MODEL` y `MAX_TOKENS`.  | Pendiente |
| Cambiar el límite de caracteres | Fácil: variable `MAX_CARACTERES`; los tests usan ese valor y no un número fijo. | Pendiente |
| Cambiar el texto de las instrucciones a la IA | Fácil: un único `SYSTEM_PROMPT` en `ai_client.py`. | Pendiente |
| Añadir un nuevo código de error | Pendiente | Pendiente |

**Conclusión sobre la mantenibilidad:** Pendiente.

## 5. Utilidad de la IA

| Aspecto | App 1 | App 2 |
|---|---|---|
| Uso de la IA | Consultas puntuales registradas en `docs/uso-ia.md`: aprender pytest y mocks, diagnosticar el error 402, borrador de la ERS y diagramas. El código lo escribió el equipo. | Desarrollo guiado por Spec Kit 1.2.4.dev0 con el agente Claude Code: especificación, plan, tareas y todo el código. |
| Dónde ayudó | Entender conceptos nuevos (mocks, entorno de Python), diagnosticar el 402 y estructurar la ERS. | Generó la especificación, el plan y 41 tareas en unos 6 min, y la implementación completa con 59 pruebas en unos 11 min. Añadió por su cuenta descartar la respuesta si se cierra sesión durante la espera. |
| Dónde falló o hubo que corregirla | Pendiente | Plan desfasado respecto a las librerías reales (Clerk, Node, Python). No cargaba `.env` y sus propias pruebas no lo detectaron. Propuso otro modelo distinto del ya probado. |
| Decisiones que mantuvo el equipo | Alcance mínimo, contrato, límites (500 caracteres, 25 s, 600 tokens) y cambio a Gemini. | Mismo modelo y límites que la App 1, mismos 12 géneros, aceptar `<Show>` y `node:22`. La verificación con PyJWT y JWKS está pendiente de revisión por Mario. |

**Conclusión sobre la utilidad de la IA:** Pendiente.

## 6. Escenarios de aceptación comunes

Los mismos escenarios se comprueban en las dos apps para comparar el flujo base. En App 2 se ejecutan con sesión iniciada.

| Escenario | Resultado esperado | App 1 | App 2 |
|---|---|---|---|
| Géneros y texto válidos | 200 con recomendaciones en la misma pantalla | Cumple | Cumple en local (PR-13, PR-16) |
| Solo géneros | 200 con recomendaciones | Cumple | Cumple en local (PR-16) |
| Sin géneros ni texto | El frontend no envía y muestra el aviso | Cumple | Cumple en local (PR-16) |
| Texto de 501 caracteres | 422 | Cumple | Cumple (`test_validation.py`) |
| La IA tarda demasiado (simulado) | 504 `TIMEOUT` | Cumple | Cumple (`test_ai_errors.py`) |
| La IA falla (simulado) | 502 `IA_NO_DISPONIBLE` | Cumple | Cumple (`test_ai_errors.py`) |
| Petición sin sesión (solo App 2) | 401 sin llamar a la IA | No aplica | Cumple (`test_auth.py` y PR-21 en local) |

## 7. Conclusiones

Pendiente: se redactarán con los datos reales de las dos apps, sin dar por hecho que una es mejor que la otra.
