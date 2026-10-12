# Pruebas de Musicfy

## Objetivo

Comprobar que el backend responde correctamente en cada situación,
sin llamar a la IA real. Todas las pruebas usan una IA simulada (mock),
así que no gastan créditos ni necesitan conexión con OpenRouter.

## Casos de prueba previstos

| Nº | Situación | Resultado esperado | Estado |
|----|-----------|--------------------|--------|
| 1 | Se envían unos gustos válidos | Responde 200 con recomendaciones y consulta a la IA una sola vez | Pendiente |
| 2 | No se envía el campo `tastes` | Responde 422 y no consulta a la IA | Pendiente |
| 3 | `tastes` está vacío o solo tiene espacios | Responde 422 y no consulta a la IA | Pendiente |
| 4 | `tastes` tiene justo el máximo de caracteres | Responde 200 | Pendiente |
| 5 | `tastes` supera el máximo de caracteres | Responde 422 y no consulta a la IA | Pendiente |
| 6 | La IA devuelve un error | Responde 502 con un mensaje claro, sin detalles internos | Pendiente |
| 7 | La IA tarda demasiado | Responde 504 | Pendiente |
| 8 | La IA devuelve una respuesta vacía o con formato incorrecto | Responde 502 en lugar de fallar | Pendiente |

## Pendiente de acordar con el grupo

- Máximo de caracteres para `tastes`.
- Tiempo máximo de espera a la IA (timeout).

## Cómo ejecutar las pruebas

Se completará cuando estén escritas.

## Resultados

Se completará con fecha, comando y resultado de cada ejecución.