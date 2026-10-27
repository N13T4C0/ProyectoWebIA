<!--
Sync Impact Report
- Version change: (plantilla sin rellenar) → 1.0.0
- Modified principles (placeholder → nombre definitivo):
  - [PRINCIPLE_1_NAME] → I. Secretos solo en el backend (NO NEGOCIABLE)
  - [PRINCIPLE_2_NAME] → II. Sin persistencia
  - [PRINCIPLE_3_NAME] → III. Contrato fijo de la API
  - [PRINCIPLE_4_NAME] → IV. Autenticación antes que todo (NO NEGOCIABLE)
  - [PRINCIPLE_5_NAME] → V. Pruebas con pytest sin servicios reales
- Added sections:
  - Principio VI. Alcance mínimo (la plantilla traía cinco; el usuario pidió seis)
  - Restricciones técnicas y de seguridad ([SECTION_2_NAME])
  - Flujo de desarrollo y puertas de calidad ([SECTION_3_NAME])
  - Gobernanza completa
- Removed sections: ninguna
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ sin cambios (lee la constitución en tiempo de ejecución)
  - .specify/templates/spec-template.md ✅ sin cambios
  - .specify/templates/tasks-template.md ✅ sin cambios
- Follow-up TODOs:
  - PEN-04 de la ERS: confirmar el código `NO_AUTORIZADO` y su mensaje; si cambia, enmienda PATCH.
  - PEN-02 de la ERS: nombres de las variables de entorno de Clerk (frontend y backend).
-->

# Musicfy App 2 Constitution

Musicfy App 2 es un recomendador musical con IA en una sola pantalla. Frontend SPA en Vue.js
con Tailwind CSS, backend en Python con FastAPI, IA con la API de Gemini de Google y
autenticación con Clerk. La fuente de requisitos es la ERS de App 2 (actualmente
`docs/ERS-app2.md` en la raíz del repositorio).

## Core Principles

### I. Secretos solo en el backend (NO NEGOCIABLE)

- La clave de la API de Gemini (`GEMINI_API_KEY`) y cualquier clave secreta de Clerk MUST
  existir únicamente en el backend y leerse de variables de entorno.
- En el frontend la única clave permitida es la publishable key de Clerk. El frontend MUST NOT
  llamar directamente a la API de Gemini.
- Los archivos `.env` MUST NOT versionarse: `.env` figura en `.gitignore` y en `.dockerignore`.
  Solo se versiona `.env.example` con valores ficticios.
- Las claves, los tokens de sesión y las trazas MUST NOT aparecer en respuestas de error,
  registros técnicos, el paquete compilado del frontend, el historial de Git ni las imágenes
  Docker.

**Justificación:** una clave filtrada permite el uso no autorizado de la IA y de Clerk a costa
del equipo; RES-05 y RNF-01 de la ERS lo exigen y PR-14 lo comprueba.

### II. Sin persistencia

- El sistema MUST NOT usar bases de datos de ningún tipo.
- Las entradas (`tastes`) y los resultados MUST NOT guardarse en disco, memoria compartida
  entre peticiones, registros, la sesión de Clerk, `localStorage`, `sessionStorage` ni
  IndexedDB.
- No existe gestión de usuarios propia: la identidad la gestiona Clerk en exclusiva.
- Los datos solo existen en memoria mientras se procesa y se muestra cada consulta; al cerrar
  sesión el resultado mostrado se borra de la pantalla.

**Justificación:** prohibición expresa del enunciado (RES-04) y requisito de privacidad RNF-03.

### III. Contrato fijo de la API

- El backend expone una única ruta funcional: `POST /api/recommend` con cuerpo
  `{"tastes": "<texto>"}` y cabecera `Authorization: Bearer <token>`.
- Éxito: `200` con `{"resultado": "<texto>"}`.
- Error: siempre `{"error": {"codigo": "<CODIGO>", "mensaje": "<texto comprensible>"}}` con
  estos y solo estos casos:
  - `401` `NO_AUTORIZADO`: token ausente, mal formado, con firma inválida, de otro emisor o
    caducado.
  - `422` `VALIDACION`: `tastes` ausente, vacío, solo espacios o con más de 500 caracteres
    tras eliminar espacios iniciales y finales.
  - `502` `IA_NO_DISPONIBLE` (fallo de conexión o error del proveedor) o `RESPUESTA_INVALIDA`
    (respuesta sin texto utilizable).
  - `504` `TIMEOUT`: la IA no responde dentro de `AI_TIMEOUT_SECONDS` (25 s por defecto).
  - `500` `ERROR_INTERNO`: cualquier error inesperado.
- Cada petición autenticada y válida MUST producir exactamente una llamada a la IA.
- El contrato MUST NOT cambiar (campos, códigos HTTP ni códigos de error) sin enmendar antes la
  ERS y esta constitución. Los errores de validación propios de FastAPI MUST adaptarse a este
  formato.

**Justificación:** el contrato es compartido con la App 1 y es lo que comprueban las pruebas
automáticas; un formato único simplifica el frontend y evita filtrar detalles internos.

### IV. Autenticación antes que todo (NO NEGOCIABLE)

- El backend MUST verificar el token de sesión de Clerk **antes** de validar la entrada y
  **antes** de llamar a la IA. Una petición sin token válido recibe `401` aunque su cuerpo sea
  inválido, y la IA MUST NOT ser llamada.
- La verificación MUST comprobar firma, emisor y caducidad mediante el SDK oficial de Clerk o
  las claves públicas del emisor (JWKS). Decodificar el token sin verificarlo no es suficiente.
- Ocultar o deshabilitar el botón en el frontend no sustituye a la verificación del backend.
- El token MUST NOT guardarse, registrarse ni enviarse a la IA, y a la IA no se le envían datos
  de identidad del usuario.

**Justificación:** impide el uso anónimo del servicio de IA (RF-06, RNF-05, OBJ-05); el orden
verificar → validar → IA garantiza que nunca se consume cuota sin una sesión válida.

### V. Pruebas con pytest sin servicios reales

- Las pruebas automáticas del backend MUST usar pytest y ejecutarse con `python -m pytest`.
- La API de Gemini y el verificador de tokens de Clerk MUST simularse con mocks. Las pruebas
  automáticas MUST NOT realizar llamadas de red a Gemini ni a Clerk ni requerir claves reales.
- MUST existir pruebas, como mínimo, para: éxito (200 y una sola llamada a la IA), cada caso de
  `422`, el límite de 500/501 caracteres, el recorte de espacios, `401` sin token, con token
  inválido y con token caducado (verificando que la IA no se llama), `502` en sus dos variantes
  y `504`.
- Toda la suite MUST pasar antes de integrar cambios en `main`.
- Las pruebas con servicios reales (Gemini y Clerk) son manuales (PR-13, PR-21) y se registran
  en la documentación de pruebas.

**Justificación:** RES-06 lo exige; las pruebas deben ser deterministas, gratuitas y
ejecutables sin secretos.

### VI. Alcance mínimo

- Una sola pantalla, un solo formulario, una sola función y una sola API de IA.
- MUST NOT añadirse nada que no esté en la ERS: ni pantallas, ni rutas de navegación del
  frontend, ni páginas de login/registro/perfil, ni endpoints, ni funciones extra (historial,
  favoritos, reproducción, enlaces a streaming, otras APIs, paneles, estadísticas, pagos,
  correo, colas, subida de archivos).
- El acceso de Clerk se integra como componente o modal en la misma pantalla.
- Las únicas rutas de backend permitidas son `POST /api/recommend` y la ruta técnica
  `GET /health` (INT-03, sin autenticación), ambas definidas en la ERS.
- Cualquier ampliación MUST incorporarse primero a la ERS; si no está en la ERS, no se
  implementa.

**Justificación:** regla obligatoria de simplicidad del enunciado (RES-03) y control del
alcance en un proyecto académico con plazo fijo.

## Restricciones técnicas y de seguridad

- **Pila obligatoria:** frontend SPA en Vue.js + Tailwind CSS; backend Python + FastAPI; IA con
  la API de Gemini (punto de acceso compatible con OpenAI); identidad con Clerk.
- **Configuración del backend por variables de entorno:** `GEMINI_API_KEY`, `GEMINI_URL`,
  `GEMINI_MODEL`, `MAX_TOKENS`, `AI_TIMEOUT_SECONDS`, `MAX_CARACTERES` y las variables de
  Clerk que se definan (PEN-02 de la ERS).
- **Presentación segura:** el frontend MUST mostrar el resultado de la IA como texto plano
  (nunca `v-html`) y sin ejecutar contenido devuelto.
- **CORS** limitado a los orígenes del frontend (local, Vercel y EC2) y permitiendo la cabecera
  `Authorization`. CORS no se considera un mecanismo de autenticación.
- **Despliegue:** Vercel y AWS EC2 con Docker, siempre por HTTPS en los entornos desplegados.
- **Accesibilidad:** formulario y acceso de Clerk utilizables con teclado y sin desplazamiento
  horizontal a 320 px (RNF-04).

## Flujo de desarrollo y puertas de calidad

- Proyecto nuevo guiado por Spec Kit: la especificación, el plan y las tareas MUST estar en Git
  antes que el código. No se copia la implementación de App 1.
- Cada plan (`/speckit-plan`) MUST incluir una comprobación explícita contra los principios
  I–VI; cualquier desviación se justifica por escrito o se rechaza.
- Antes de integrar en `main`: suite de pytest en verde, ningún secreto en el diff y ninguna
  funcionalidad ajena a la ERS.
- Cada revisión de código comprueba, como mínimo, el orden verificar token → validar → IA, el
  formato de error del contrato y la ausencia de persistencia.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica del proyecto. En caso de conflicto
  con la ERS, se corrige el documento que esté desfasado mediante acuerdo del equipo.
- **Enmiendas:** se proponen por escrito, las aprueban los tres integrantes del equipo y se
  registran en Git con un informe de impacto y el cambio de versión correspondiente.
- **Versionado semántico:** MAJOR para eliminar o redefinir principios de forma incompatible;
  MINOR para añadir principios o secciones o ampliar materialmente su contenido; PATCH para
  aclaraciones y correcciones de redacción.
- **Cumplimiento:** toda especificación, plan, lista de tareas y revisión de código MUST
  verificar el cumplimiento de esta constitución. La complejidad añadida MUST justificarse.

**Version**: 1.0.0 | **Ratified**: 2026-10-25 | **Last Amended**: 2026-10-25
