export const GENEROS = [
  'Indie',
  'Rock',
  'Pop',
  'Electrónica',
  'Hip hop',
  'Flamenco',
  'Jazz',
  'Metal',
  'R&B',
  'Reggaetón',
  'Clásica',
  'Lo-fi',
]

// Composición de `tastes` según data-model.md.
export function composeTastes(generos, texto) {
  const libre = texto.trim()
  if (generos.length === 0) return libre
  const lista = `Géneros: ${generos.join(', ')}.`
  return libre ? `${lista} Además: ${libre}` : lista
}

// Devuelve { status, data }; un fallo de red se indica con { status: 0, data: null }.
export async function recommend(tastes, token) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL ?? ''}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ tastes }),
    })
    const data = await response.json().catch(() => null)
    return { status: response.status, data }
  } catch {
    return { status: 0, data: null }
  }
}
