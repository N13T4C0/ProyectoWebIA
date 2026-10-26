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
| Análisis y requisitos (ERS / especificación de Spec Kit) | Pendiente (estimación) | Pendiente |
| Backend (FastAPI, validación, llamada a la IA, errores) | Pendiente (estimación) | Pendiente |
| Frontend (formulario, estados, Tailwind) | Pendiente (estimación) | Pendiente |
| Pruebas con pytest y mocks | Pendiente (estimación) | Pendiente |
| Revisión y corrección de propuestas de la IA | No aplica: App 1 se construyó manualmente | Pendiente |
| Documentación | Pendiente (estimación) | Pendiente |
| **Total del flujo base** | **Pendiente** | **Pendiente** |

**Esfuerzo separado (no se suma al flujo base):**

| Tarea | App 1 | App 2 |
|---|---|---|
| Autenticación con Clerk | No aplica | Pendiente |
| Despliegue en Vercel | Pendiente (estimación) | Pendiente |
| Docker en local | No aplica | Pendiente |
| AWS EC2 con HTTPS | No aplica | Pendiente |

**Conclusión sobre el tiempo:** Pendiente.

## 2. Calidad

| Aspecto | App 1 | App 2 |
|---|---|---|
| Legibilidad del código | Pendiente | Pendiente |
| Validaciones de la entrada | Validación en backend con Pydantic (vacío, solo espacios, más de 500 caracteres) y en el frontend (sin géneros ni texto no se envía). | Pendiente |
| Contrato JSON | `{"tastes"}` → `{"resultado"}` o `{"error": {"codigo", "mensaje"}}`, estable desde el principio. | Pendiente |
| Tratamiento de errores | 422, 502 (`IA_NO_DISPONIBLE`, `RESPUESTA_INVALIDA`), 504 (`TIMEOUT`) y 500 (`ERROR_INTERNO`), sin detalles internos. | Pendiente (añade 401 `NO_AUTORIZADO`) |
| Pruebas automáticas | 12 tests con pytest y mocks de la IA, todos en verde (13/10/2026). | Pendiente |
| Consistencia con la ERS | Trazabilidad completa en `docs/ERS.md` (versión 1.0). | Pendiente |

**Conclusión sobre la calidad:** Pendiente.

## 3. Errores

Problemas concretos encontrados, su origen y su solución.

### App 1

| Fecha | Problema | Origen | Solución |
|---|---|---|---|
| 12/10/2026 | Entorno de Python duplicado y carpetas reorganizadas a mitad del trabajo (`app1-Musicfy`). | Falta de acuerdo inicial sobre la ubicación del entorno y la estructura. | Volver a clonar el repositorio y crear un único entorno en `backend/.venv`. |
| 13/10/2026 | La petición válida devolvía 502 «El servicio de IA ha respondido con un error». | OpenRouter respondía 402: sin `max_tokens`, reservaba saldo para la respuesta máxima del modelo y la cuenta no tenía suficiente. | Limitar `MAX_TOKENS` a 600. Diagnosticado con un script que mostraba el código real de OpenRouter. |
| 19/10/2026 | Las peticiones a la IA fallaban en el despliegue de Vercel. | Pendiente | Cambio de proveedor a la API de Gemini de Google. Pendiente de detallar. |
| 19/10/2026 | Los commits de algunos integrantes aparecen bloqueados por Vercel en GitHub. | El proyecto de Vercel pertenece a un solo integrante y no admite despliegues de commits de otros autores. | No afecta a la app desplegada. Pendiente de decidir si se cambia la configuración. |

### App 2

| Fecha | Problema | Origen | Solución |
|---|---|---|---|
| Pendiente | Pendiente | Pendiente | Pendiente |

**Conclusión sobre los errores:** Pendiente.

## 4. Mantenibilidad

Qué cambio pequeño sería fácil o difícil en cada app y por qué. Son ejemplos para razonar; no se implementan como nuevas funciones.

| Cambio hipotético | App 1 | App 2 |
|---|---|---|
| Cambiar el modelo o el proveedor de IA | Fácil en la práctica: se hizo de OpenRouter a Gemini cambiando `config.py`, `ai_client.py` y las variables de entorno; los tests no cambiaron porque simulan `ask_model`. | Pendiente |
| Cambiar el límite de caracteres | Fácil: variable `MAX_CARACTERES`; los tests usan ese valor y no un número fijo. | Pendiente |
| Cambiar el texto de las instrucciones a la IA | Fácil: un único `SYSTEM_PROMPT` en `ai_client.py`. | Pendiente |
| Añadir un nuevo código de error | Pendiente | Pendiente |

**Conclusión sobre la mantenibilidad:** Pendiente.

## 5. Utilidad de la IA

| Aspecto | App 1 | App 2 |
|---|---|---|
| Uso de la IA | Consultas puntuales registradas en `docs/uso-ia.md`: aprender pytest y mocks, diagnosticar el error 402, borrador de la ERS y diagramas. El código lo escribió el equipo. | Desarrollo guiado por Spec Kit con el agente Pendiente. |
| Dónde ayudó | Entender conceptos nuevos (mocks, entorno de Python), diagnosticar el 402 y estructurar la ERS. | Pendiente |
| Dónde falló o hubo que corregirla | Pendiente | Pendiente (propuestas rechazadas: bases de datos, pantallas extra, etc.) |
| Decisiones que mantuvo el equipo | Alcance mínimo, contrato, límites (500 caracteres, 25 s, 600 tokens) y cambio a Gemini. | Pendiente |

**Conclusión sobre la utilidad de la IA:** Pendiente.

## 6. Escenarios de aceptación comunes

Los mismos escenarios se comprueban en las dos apps para comparar el flujo base. En App 2 se ejecutan con sesión iniciada.

| Escenario | Resultado esperado | App 1 | App 2 |
|---|---|---|---|
| Géneros y texto válidos | 200 con recomendaciones en la misma pantalla | Cumple | Pendiente |
| Solo géneros | 200 con recomendaciones | Cumple | Pendiente |
| Sin géneros ni texto | El frontend no envía y muestra el aviso | Cumple | Pendiente |
| Texto de 501 caracteres | 422 | Cumple | Pendiente |
| La IA tarda demasiado (simulado) | 504 `TIMEOUT` | Cumple | Pendiente |
| La IA falla (simulado) | 502 `IA_NO_DISPONIBLE` | Cumple | Pendiente |
| Petición sin sesión (solo App 2) | 401 sin llamar a la IA | No aplica | Pendiente |

## 7. Conclusiones

Pendiente: se redactarán con los datos reales de las dos apps, sin dar por hecho que una es mejor que la otra.
