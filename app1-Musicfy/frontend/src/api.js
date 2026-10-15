// Única comunicación del frontend con el backend (FastAPI).
// Contrato acordado: POST /api/recommend  ->  {"tastes": "..."}
// Respuesta 200: {"resultado": "..."}
// Errores: 422 (validación de FastAPI) o {"error": {"codigo": "...", "mensaje": "..."}}

export const MAX_CARACTERES = 500 // Pendiente de confirmar con backend

// En desarrollo el backend va aparte (localhost:8000); en producción va en el mismo dominio (/api)
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '')).replace(/\/$/, '')
const USAR_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const TIMEOUT_MS = 30000

export class ApiError extends Error {
  constructor(codigo, mensaje) {
    super(mensaje)
    this.codigo = codigo
    this.mensaje = mensaje
  }
}

export async function recomendar(tastes) {
  if (USAR_MOCK) return recomendarMock(tastes)

  const controller = new AbortController()
  const temporizador = setTimeout(() => controller.abort(), TIMEOUT_MS)

  let res
  try {
    res = await fetch(`${BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tastes }),
      signal: controller.signal,
    })
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new ApiError('TIMEOUT', 'El servidor ha tardado demasiado. Inténtalo más tarde.')
    }
    throw new ApiError('SIN_CONEXION', 'No se ha podido conectar con el servidor.')
  } finally {
    clearTimeout(temporizador)
  }

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    if (data?.error?.mensaje) {
      throw new ApiError(data.error.codigo ?? 'ERROR', data.error.mensaje)
    }
    if (res.status === 422) {
      throw new ApiError('VALIDACION', 'El texto no es válido. Revisa que no esté vacío ni supere el límite.')
    }
    throw new ApiError('ERROR', 'No se ha podido completar la petición. Inténtalo más tarde.')
  }

  if (typeof data?.resultado !== 'string' || !data.resultado.trim()) {
    throw new ApiError('RESPUESTA_INVALIDA', 'La respuesta no tiene el formato esperado.')
  }

  return { resultado: data.resultado }
}

//  Mock de pruebra para desarrollar sin backend (VITE_USE_MOCK=true) 
async function recomendarMock(tastes) {
  await new Promise((r) => setTimeout(r, 1200))

  if (tastes.toLowerCase().includes('#error')) {
    throw new ApiError('IA_NO_DISPONIBLE', 'No se ha podido completar la petición. Inténtalo más tarde.')
  }

  return {
    resultado:
      '[RESPUESTA SIMULADA, NO VIENE DE LA IA]\n\n' +
      '1. Artista de prueba A: comparte el sonido que describes.\n' +
      '2. Artista de prueba B: misma época y energía parecida.\n' +
      '3. Artista de prueba C: una opción algo más arriesgada.',
  }
}
