# Pruebas de Musicfy

## Objetivo

Comprobar que el backend responde correctamente en cada situación,
sin llamar a la IA real. Las pruebas automáticas usan una IA simulada (mock),
así que no gastan créditos ni necesitan conexión con OpenRouter.

## Entorno

- Python: 3.14.5
- pytest: 9.1.1
- Sistema: Windows

## Cómo ejecutar las pruebas

Desde la carpeta `backend`, con el entorno activado:

    python -m pytest

No hace falta tener el backend arrancado ni clave de OpenRouter.

## Límites que se comprueban

- Máximo de caracteres para `tastes`: 500
- Tiempo máximo de espera a la IA: 25 segundos
- Máximo de tokens solicitados a OpenRouter: 600 (configurable con `MAX_TOKENS`)

## Casos de prueba

| Nº | Situación | Resultado esperado | Test | Estado |
|----|-----------|--------------------|------|--------|
| 1 | Se consulta `/health` | Responde 200 con `status: ok` | `test_health_responde_ok` | Hecho |
| 2 | Se envían unos gustos válidos | Responde 200 y consulta a la IA una sola vez | `test_texto_valido_devuelve_recomendacion` | Pendiente |
| 3 | No se envía el campo `tastes` | Responde 422 | `test_sin_campo_tastes_da_422` | Hecho |
| 4 | `tastes` está vacío | Responde 422 y no consulta a la IA | `test_texto_vacio_da_422`, `test_texto_vacio_no_llama_a_la_ia` | Pendiente |
| 5 | `tastes` solo tiene espacios | Responde 422 | `test_texto_solo_espacios_da_422` | Hecho |
| 6 | `tastes` tiene justo 500 caracteres | Responde 200 | `test_texto_justo_en_el_limite_funciona` | Pendiente |
| 7 | `tastes` tiene 501 caracteres | Responde 422 | `test_texto_demasiado_largo_da_422` | Hecho |
| 8 | La IA tarda demasiado | Responde 504 con código `TIMEOUT` | `test_ia_tarda_demasiado_da_504` | Pendiente |
| 9 | La IA falla | Responde 502 con código `IA_NO_DISPONIBLE` | `test_ia_falla_da_502` | Pendiente |
| 10 | La IA responde algo con formato incorrecto | Responde 502 con código `RESPUESTA_INVALIDA` | `test_ia_responde_algo_roto_da_502` | Pendiente |

## Resultados de ejecución

| Fecha | Comando | Resultado |
|-------|---------|-----------|
| 13/10/2026 | `python -m pytest` | 1 passed |
| 13/10/2026 | `python -m pytest` | 5 passed |



## Pruebas manuales con la IA real

Además de las automáticas, se ha probado a mano desde `/docs` con OpenRouter real:

- 13/10/2026: la petición válida devolvía 502. Con un script de diagnóstico se vio
  que OpenRouter respondía 402 por falta de créditos. El backend limita ahora la
  respuesta mediante `MAX_TOKENS` (600 por defecto), pero un 402 sigue requiriendo
  añadir saldo o usar un modelo disponible en la cuenta de OpenRouter.

## Observaciones

- Al ejecutar pytest con el primer test aparece un aviso de deprecación de Starlette sobre `httpx`.
  No afecta a los resultados; pendiente de revisar al actualizar dependencias.