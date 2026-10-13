// Detecta los nombres de artistas dentro del texto de la IA para pintarlos de otro color.
// Es una heurística: si una línea no encaja con ningún patrón se muestra tal cual.
// Devuelve una lista de líneas; cada línea es una lista de trozos { texto, artista }.

const MAX_LARGO_NOMBRE = 60

// "Artista: Radiohead", "2. Nombre del artista o banda: Radiohead", "- Banda: Radiohead"
const PATRON_ETIQUETA = /^(\s*(?:\d+[.)]|[-•*])?\s*(?:nombre del )?(?:artista|banda|grupo)(?: o (?:banda|grupo))?\s*:\s*)(.+)$/i

// "1. Radiohead - explicación…", "2) Radiohead: explicación…",
// "* Radiohead: explicación…" (viñetas solo sin sangría: las sangradas son detalles)
const PATRON_LISTA = /^(\s*\d+[.)]\s+|[-•*]\s+)(.+)$/

// Separadores habituales entre el nombre y la explicación
const SEPARADOR = /\s+[-–—]\s+|:\s|\s\(/

// Etiquetas de detalle que no son nombres ("- Canción sugerida: …")
const NO_ES_ARTISTA = /^(canci[oó]n|[aá]lbum|disco|tema|por qu[eé]|motivo|explicaci[oó]n|recomendaci[oó]n|para empezar|empieza|escucha|g[eé]nero|[eé]poca)/i

function trozo(texto, artista = false) {
  return { texto, artista }
}

function lineaConNombre(prefijo, nombre, resto) {
  nombre = nombre.trim()
  if (!nombre || nombre.length > MAX_LARGO_NOMBRE || NO_ES_ARTISTA.test(nombre)) {
    return [trozo(prefijo + nombre + resto)]
  }
  return [trozo(prefijo), trozo(nombre, true), trozo(resto)].filter((t) => t.texto)
}

function segmentarLinea(linea) {
  const etiqueta = linea.match(PATRON_ETIQUETA)
  if (etiqueta) return lineaConNombre(etiqueta[1], etiqueta[2], '')

  const lista = linea.match(PATRON_LISTA)
  if (lista) {
    const [, prefijo, contenido] = lista
    const corte = contenido.search(SEPARADOR)
    if (corte === -1) return lineaConNombre(prefijo, contenido, '')
    return lineaConNombre(prefijo, contenido.slice(0, corte), contenido.slice(corte))
  }

  return [trozo(linea)]
}

export function resaltarArtistas(texto) {
  // El modelo a veces marca en negrita con ** aunque se le pida texto plano
  return texto.replaceAll('**', '').split('\n').map(segmentarLinea)
}
