# Contrato de la pantalla única (IU-01)

Una sola pantalla, sin router ni rutas adicionales.

## Elementos

| Elemento | Requisitos |
|---|---|
| Título «Musicfy» | Siempre visible. |
| Acceso de Clerk | Sin sesión: `SignInButton` en modo modal. Con sesión: `UserButton` (cerrar sesión). Alcanzable con tabulador. |
| Grupo de géneros | `role="group"` con `aria-label="Géneros musicales"`. 12 botones: Indie, Rock, Pop, Electrónica, Hip hop, Flamenco, Jazz, Metal, R&B, Reggaetón, Clásica, Lo-fi. `aria-pressed` y marca ✓ visible cuando están seleccionados. |
| Campo de texto | `<label>` visible asociado («¿Qué música te gusta?»). |
| Botón «Recomendar» | Deshabilitado sin sesión y durante la espera. |
| Mensaje de validación local | «Elige algún género o escribe algo sobre la música que te gusta» si no hay géneros ni texto; no se envía nada. |
| Indicador de espera | Visible solo durante la petición (`aria-live="polite"`). |
| Zona de resultado | Texto plano con `whitespace-pre-line` y `break-words`; nunca `v-html`. Sustituye al anterior. |
| Zona de error | `error.mensaje` del backend; ante 401, además invita a iniciar sesión de nuevo. Sin conexión con el backend: mensaje genérico de servicio no disponible. |

## Comportamiento

- Antes de cada envío se obtiene un token nuevo con `getToken()` y se manda en
  `Authorization: Bearer`.
- Al cerrar sesión se borran resultado, error y estado de espera.
- Nada se guarda en `localStorage`, `sessionStorage` ni IndexedDB.
- Diseño de una columna, foco visible en todos los controles y sin desplazamiento horizontal a
  320 px.
