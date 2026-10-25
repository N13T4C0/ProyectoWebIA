# Feature Specification: Musicfy App 2 — recomendador musical con IA y autenticación

**Feature Branch**: `001-musicfy-recomendador`

**Created**: 2026-10-25

**Status**: Draft

**Input**: User description: "Construir Musicfy App 2 según la ERS en ../app1-Musicfy/docs/ERS-app2.md. Léela entera y respeta sus requisitos (RF-01 a RF-06 y RNF), restricciones, casos de uso y criterios de aceptación. No añadas nada que no esté en la ERS."

**Fuente de requisitos**: ERS de App 2, versión 0.1 (`../app1-Musicfy/docs/ERS-app2.md`). Cada
requisito de esta especificación indica entre paréntesis el identificador de la ERS del que
procede. Esta especificación no añade funciones que no estén en la ERS.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener recomendaciones con la sesión iniciada (Priority: P1)

Una persona que ya ha iniciado sesión elige uno o varios géneros musicales y/o escribe con sus
palabras qué música le gusta, pulsa enviar y, en la misma pantalla, recibe un texto con unas
pocas recomendaciones explicadas (CU-01, flujo principal; RF-01, RF-03, RF-04).

**Why this priority**: es la única función útil de la aplicación (OBJ-01). Sin ella no hay
producto.

**Independent Test**: con una sesión válida y la IA simulada respondiendo correctamente, enviar
géneros y texto y comprobar que el resultado aparece en la misma pantalla y que la IA se ha
consultado una sola vez con el texto del usuario.

**Acceptance Scenarios**:

1. **Given** un usuario con sesión iniciada que ha seleccionado géneros y escrito un texto,
   **When** pulsa enviar, **Then** se envía una única petición con los gustos compuestos y la
   credencial de sesión (CA-RF01-01).
2. **Given** un usuario con sesión iniciada que solo ha seleccionado géneros, **When** pulsa
   enviar, **Then** la petición contiene esos géneros (CA-RF01-02).
3. **Given** una petición en curso, **When** el usuario vuelve a pulsar enviar, **Then** no se
   envía una segunda petición (CA-RF01-03).
4. **Given** una sesión válida, un texto válido y una IA que responde correctamente, **When**
   se envía, **Then** el sistema responde con éxito y el resultado de la IA, y la IA se ha
   consultado exactamente una vez con el texto del usuario (CA-RF03-01, CA-RF06-04).
5. **Given** un texto con espacios al principio y al final, **When** se envía, **Then** la IA
   recibe el texto sin esos espacios (CA-RF03-02).
6. **Given** un envío autenticado y válido, **When** llega el resultado, **Then** el texto
   aparece en la misma pantalla, sin navegar a otra (CA-RF04-01).
7. **Given** un resultado previo en pantalla, **When** se hace una nueva consulta, **Then**
   solo se muestra el nuevo resultado (CA-RF04-02).
8. **Given** una respuesta que contiene etiquetas HTML, **When** se muestra, **Then** aparecen
   como texto y no se interpretan (CA-RF04-03).

---

### User Story 2 - Iniciar y cerrar sesión y proteger el servicio (Priority: P1)

La persona inicia y cierra sesión en la misma pantalla con el servicio de identidad externo
(Clerk). Sin una sesión válida no puede pedir recomendaciones, y el servidor rechaza cualquier
petición sin credencial válida —incluidas las llamadas directas que no pasan por la pantalla—
sin consultar a la IA (RF-06, RNF-05, CU-01 A1).

**Why this priority**: es el requisito nuevo de la App 2 y es obligatorio (OBJ-05, RES-10).
Comparte prioridad con la historia 1 porque la recomendación solo se ofrece con sesión.

**Independent Test**: con el verificador de credenciales simulado, enviar peticiones sin
credencial, con credencial inválida y con credencial caducada y comprobar que todas reciben
«no autorizado» y que la IA simulada no se llama.

**Acceptance Scenarios**:

1. **Given** una petición sin credencial de sesión, **When** llega al servidor, **Then**
   responde «no autorizado» (`NO_AUTORIZADO`) y no consulta a la IA (CA-RF06-01).
2. **Given** una credencial inválida (firma incorrecta, mal formada o de otro emisor), **When**
   se envía, **Then** el servidor responde «no autorizado» y no consulta a la IA (CA-RF06-02).
3. **Given** una credencial caducada, **When** se envía, **Then** el servidor responde «no
   autorizado» y no consulta a la IA (CA-RF06-03).
4. **Given** una credencial válida y un texto válido, **When** se envía, **Then** la petición
   continúa y se responde con éxito (CA-RF06-04).
5. **Given** un usuario sin sesión, **When** abre la aplicación, **Then** ve el acceso de Clerk
   en la misma pantalla y no puede enviar el formulario; tras iniciar sesión puede enviarlo, y
   tras cerrar sesión deja de poder hacerlo (CA-RF06-05).
6. **Given** un resultado en pantalla, **When** el usuario cierra sesión, **Then** el resultado
   deja de mostrarse (CA-RF04-04).
7. **Given** que el servidor responde «no autorizado», **When** la pantalla recibe la
   respuesta, **Then** informa de que hay que iniciar sesión de nuevo (RF-04, CU-01 A1).

---

### User Story 3 - Rechazar entradas no válidas sin consultar a la IA (Priority: P2)

Si el formulario está vacío, la pantalla avisa sin enviar nada. Si llega al servidor una
petición autenticada con gustos ausentes, vacíos, formados solo por espacios o de más de 500
caracteres, el servidor la rechaza con un error de validación y no consulta a la IA (RF-01,
RF-02, CU-01 A0 y A2).

**Why this priority**: protege la cuota de la IA y orienta al usuario (OBJ-02), pero depende
de que exista la función principal.

**Independent Test**: con una credencial válida simulada, enviar los casos límite de entrada y
comprobar el código de validación y que la IA simulada no se llama.

**Acceptance Scenarios**:

1. **Given** que no hay géneros seleccionados ni texto, **When** el usuario intenta enviar,
   **Then** la pantalla muestra «Elige algún género o escribe algo sobre la música que te
   gusta» y no envía ninguna petición (CA-RF01-04).
2. **Given** una credencial válida y un texto vacío, **When** se envía, **Then** el servidor
   responde con error de validación (`VALIDACION`) y no consulta a la IA (CA-RF02-01).
3. **Given** una credencial válida y un texto formado solo por espacios, **When** se envía,
   **Then** el servidor responde con error de validación (CA-RF02-02).
4. **Given** una credencial válida y una petición sin el campo de gustos, **When** se envía,
   **Then** el servidor responde con error de validación (CA-RF02-03).
5. **Given** una credencial válida y un texto de exactamente 500 caracteres, **When** se envía,
   **Then** se acepta (CA-RF02-04).
6. **Given** una credencial válida y un texto de 501 caracteres, **When** se envía, **Then** el
   servidor responde con error de validación (CA-RF02-05).

---

### User Story 4 - Informar de fallos de la IA de forma comprensible (Priority: P2)

Cuando la IA tarda demasiado, falla o devuelve una respuesta sin texto utilizable, la persona
ve en la misma pantalla un mensaje comprensible, sin detalles internos (RF-05, RNF-02, CU-01 A3
a A5).

**Why this priority**: necesario para una experiencia fiable (OBJ-03), pero secundario respecto
a la función principal y la protección del servicio.

**Independent Test**: con la IA simulada provocando cada fallo, comprobar el código HTTP, el
código de error y la ausencia de detalles internos.

**Acceptance Scenarios**:

1. **Given** una IA que supera el tiempo máximo de espera, **When** se envía una petición
   autenticada y válida, **Then** se responde «tiempo agotado» (504, `TIMEOUT`) (CA-RF05-01).
2. **Given** una IA que falla, **When** se envía una petición autenticada y válida, **Then** se
   responde «IA no disponible» (502, `IA_NO_DISPONIBLE`) (CA-RF05-02).
3. **Given** una IA que devuelve una respuesta sin contenido utilizable, **When** se envía una
   petición autenticada y válida, **Then** se responde «respuesta inválida» (502,
   `RESPUESTA_INVALIDA`) (CA-RF05-03).
4. **Given** cualquier respuesta de error, **When** se muestra, **Then** no contiene trazas,
   claves, credenciales ni la respuesta completa del proveedor (RF-05).

---

### Edge Cases

- Petición sin credencial válida y además con gustos no válidos: se responde «no autorizado»
  (401), no «validación», porque la credencial se verifica antes que la entrada (RF-06, CU-01
  A1).
- Llamada directa al servidor sin pasar por la pantalla y sin credencial: 401 y sin consulta a
  la IA (RF-06).
- Servicio de identidad no disponible: no se puede iniciar sesión; el servidor no puede
  verificar credenciales, responde 401 y no consulta a la IA (DEP-04).
- Gustos compuestos por géneros más texto libre que superan 500 caracteres: el límite incluye
  los géneros (RF-01, DAT-01).
- Error inesperado en el servidor: 500 con `ERROR_INTERNO` y sin detalles internos (RF-05).
- Pulsar enviar repetidamente durante la espera: una sola petición (CA-RF01-03).
- Texto de respuesta muy largo: no rompe el diseño de la pantalla (RF-04).
- Recarga de la página o reinicio del servidor: no reaparece ninguna consulta ni resultado
  anterior (RNF-03).

## Requirements *(mandatory)*

### Functional Requirements

**Entrada (RF-01)**

- **FR-001**: La pantalla MUST ofrecer, a un usuario con sesión iniciada, un único formulario
  con un grupo de géneros de selección múltiple (opcional), un campo de texto libre (opcional)
  y un botón de envío.
- **FR-002**: Al enviar, la pantalla MUST componer un único texto de gustos con el formato
  `Géneros: <lista>. Además: <texto libre>`, omitiendo la parte que falte, y enviarlo junto con
  la credencial de sesión vigente.
- **FR-003**: Si no hay géneros ni texto, la pantalla MUST mostrar «Elige algún género o
  escribe algo sobre la música que te gusta» y MUST NOT enviar la petición.
- **FR-004**: Mientras haya una petición pendiente, la pantalla MUST mostrar un indicador de
  espera e impedir un segundo envío.
- **FR-005**: Sin sesión iniciada, la pantalla MUST NOT permitir enviar el formulario y MUST
  mostrar el acceso de Clerk.

**Validación (RF-02)**

- **FR-006**: El servidor MUST rechazar con error de validación (422, `VALIDACION`) toda
  petición autenticada cuyos gustos falten, estén vacíos, contengan solo espacios o superen 500
  caracteres tras eliminar los espacios iniciales y finales, sin consultar a la IA.
- **FR-007**: El límite de 500 caracteres MUST ser configurable (`MAX_CARACTERES`).
- **FR-008**: La validación de la pantalla MUST NOT sustituir a la del servidor.

**Recomendación (RF-03)**

- **FR-009**: Por cada envío autenticado y válido, el servidor MUST realizar exactamente una
  consulta al proveedor de IA (API de Gemini) con las instrucciones del recomendador y el texto
  validado sin espacios iniciales ni finales.
- **FR-010**: La consulta MUST limitar la respuesta a un máximo de tokens configurable y MUST
  tener un tiempo máximo de espera de 25 segundos, configurable (RNF-02).
- **FR-011**: Si la IA devuelve texto, el servidor MUST responder éxito (200) con ese texto
  como resultado.
- **FR-012**: El servidor MUST NOT enviar a la IA la credencial de sesión ni datos de identidad
  del usuario.

**Presentación (RF-04)**

- **FR-013**: La pantalla MUST mostrar el resultado o el mensaje de error en la misma pantalla
  del formulario, como texto plano, sustituyendo cualquier resultado anterior y sin interpretar
  HTML ni ejecutar código devuelto.
- **FR-014**: Ante una respuesta «no autorizado», la pantalla MUST informar de que hay que
  iniciar sesión de nuevo.
- **FR-015**: Al cerrar sesión, la pantalla MUST borrar el resultado mostrado.
- **FR-016**: Un texto de respuesta largo MUST NOT romper el diseño.

**Errores de la IA (RF-05)**

- **FR-017**: El servidor MUST responder 504 `TIMEOUT` si se supera el tiempo máximo; 502
  `IA_NO_DISPONIBLE` ante un fallo de conexión o un error del proveedor; 502
  `RESPUESTA_INVALIDA` si la respuesta no contiene texto utilizable; y 500 `ERROR_INTERNO` ante
  un error inesperado.
- **FR-018**: Las respuestas de error MUST NOT incluir trazas, claves, credenciales ni la
  respuesta completa del proveedor.

**Autenticación (RF-06)**

- **FR-019**: La pantalla MUST permitir iniciar y cerrar sesión con Clerk mediante un componente
  integrado o modal en la misma pantalla, sin rutas ni páginas nuevas.
- **FR-020**: El servidor MUST verificar la credencial de sesión **antes** de validar la entrada
  y antes de consultar a la IA, comprobando firma, emisor, caducidad y orígenes autorizados con
  los medios oficiales del emisor; decodificarla sin verificarla no es suficiente.
- **FR-021**: Toda petición sin credencial, o con credencial mal formada, con firma no válida,
  de otro emisor o caducada, MUST recibir 401 `NO_AUTORIZADO` sin consultar a la IA, también
  cuando la llamada no procede de la pantalla.
- **FR-022**: El sistema MUST NOT guardar usuarios, ni datos de sesión más allá de lo que
  gestiona Clerk, ni registrar o almacenar la credencial.

**Interfaz con el servidor (INT-01, INT-03)**

- **FR-023**: La única operación funcional del servidor MUST ser `POST /api/recommend`, que
  recibe `{"tastes": "..."}` con la credencial en la cabecera `Authorization: Bearer <token>` y
  responde `{"resultado": "..."}` (200) o `{"error": {"codigo": "...", "mensaje": "..."}}` con
  los códigos 401, 422, 500, 502 y 504.
- **FR-024**: El servidor MUST ofrecer la comprobación técnica de estado `GET /health`, sin
  autenticación, que responde `{"status": "ok", ...}`.
- **FR-025**: El servidor MUST aceptar peticiones solo desde los orígenes de la pantalla (local,
  Vercel y EC2), permitiendo la cabecera de autorización.

**Seguridad, privacidad y accesibilidad (RNF-01, RNF-03, RNF-04, RNF-05)**

- **FR-026**: La clave de la IA y cualquier clave secreta de Clerk MUST existir solo en la
  configuración privada del servidor; en la pantalla solo puede estar la clave publishable de
  Clerk. Los ficheros de configuración privada MUST NOT versionarse ni incluirse en las imágenes
  de contenedor; solo se versiona un ejemplo con valores ficticios.
- **FR-027**: El sistema MUST NOT conservar entradas ni resultados tras responder (ni en el
  servidor, ni en el almacenamiento del navegador, ni en la sesión de Clerk), y los registros
  técnicos MUST NOT incluir textos, respuestas, credenciales ni secretos.
- **FR-028**: El campo de texto MUST tener una etiqueta visible asociada; el grupo de géneros
  MUST tener un nombre accesible; cada género, el campo, el botón y el acceso de Clerk MUST ser
  alcanzables con el tabulador y con foco visible; el estado seleccionado de un género MUST NOT
  depender solo del color; y la página MUST NOT tener desplazamiento horizontal a 320 px.
- **FR-029**: En los despliegues (Vercel y AWS EC2 con contenedores), la aplicación MUST
  servirse por HTTPS (RES-07, RNF-05).

### Key Entities *(include if feature involves data)*

Todos los datos son transitorios: existen solo mientras se procesa y se muestra cada consulta.

- **Petición de recomendación (DAT-01)**: texto de gustos compuesto a partir de géneros y texto
  libre; obligatorio, de 1 a 500 caracteres tras eliminar espacios iniciales y finales.
- **Respuesta de recomendación (DAT-02)**: texto de resultado generado por la IA; no vacío.
- **Respuesta de error (DAT-03)**: código (uno de `VALIDACION`, `NO_AUTORIZADO`, `TIMEOUT`,
  `IA_NO_DISPONIBLE`, `RESPUESTA_INVALIDA`, `ERROR_INTERNO`) y mensaje comprensible.
- **Credencial de sesión (DAT-04)**: emitida por Clerk tras iniciar sesión; el servidor solo la
  verifica en cada petición; no se guarda, no se registra y no se envía a la IA.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con sesión iniciada y una entrada válida, el usuario ve en la misma pantalla un
  texto de recomendaciones no vacío (OBJ-01, PR-13).
- **SC-002**: El 100 % de las entradas no válidas probadas se rechazan sin ninguna consulta a la
  IA (OBJ-02, PR-02 a PR-08).
- **SC-003**: El 100 % de las peticiones sin credencial, con credencial inválida o caducada se
  rechazan como «no autorizado» sin ninguna consulta a la IA, incluidas las llamadas directas al
  servidor (OBJ-05, PR-18 a PR-21).
- **SC-004**: Si la IA no responde en 25 segundos, el usuario recibe un mensaje de error
  comprensible en lugar de una espera indefinida; los fallos de la IA producen siempre el código
  acordado sin detalles internos (OBJ-03, PR-10 a PR-12).
- **SC-005**: La inspección de la pantalla, su paquete publicado, el repositorio con su
  historial y las imágenes de contenedor no encuentra ninguna clave privada (OBJ-04, PR-14).
- **SC-006**: Tras reiniciar el servidor y recargar la pantalla no aparece ninguna consulta ni
  resultado anterior (RNF-03, PR-15).
- **SC-007**: Una persona puede completar el formulario y el acceso solo con teclado y en una
  vista de 320 px sin desplazamiento horizontal (RNF-04, PR-17).
- **SC-008**: Las dos URL desplegadas (Vercel y EC2, ambas por HTTPS) responden según el
  contrato a un caso válido y a uno de error (OBJ-06, PR-22, PR-23).
- **SC-009**: Todas las pruebas automáticas se ejecutan sin consultar servicios reales de IA ni
  de identidad (RES-06).

## Assumptions

- **Restricciones impuestas por la ERS y la constitución** (no son decisiones de esta
  especificación): pantalla SPA en Vue.js con Tailwind CSS, servidor en Python con FastAPI, IA
  con la API de Gemini en su formato compatible con OpenAI, identidad con Clerk, pruebas con
  pytest con la IA y el verificador de credenciales simulados, despliegue en Vercel y en AWS EC2
  con Docker (RES-01 a RES-11).
- Fuera de alcance (ERS 1.3): bases de datos y cualquier persistencia; historial, favoritos,
  listas o conversaciones; gestión de usuarios propia; páginas o rutas de login, registro,
  perfil o administración; reproducción de música o enlaces a streaming; otras APIs; varias
  pantallas o paneles; subida de archivos, pagos, correo, colas; servicios adicionales de AWS.
- El número (3 a 5) y el formato de las recomendaciones son instrucciones a la IA y no se
  garantizan; solo se garantiza que el resultado no esté vacío (SUP-01).
- Los textos de los mensajes de error, salvo el de formulario vacío, no los fija la ERS; serán
  mensajes comprensibles en español.
- La lista concreta de géneros ofrecidos no la fija la ERS; se definirá en el plan.
- Pendientes heredados de la ERS que no bloquean esta especificación: código y mensaje
  definitivos de `NO_AUTORIZADO` (PEN-04), nombres de las variables de configuración de Clerk
  (PEN-02), acceso a AWS y dominio HTTPS (PEN-03), URL de despliegue (PEN-06) y nombres
  definitivos de los tests (PEN-05).
- Volumen de uso de demostración académica; no se fijan cifras de capacidad (ERS 2.4).
