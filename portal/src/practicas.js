// ─────────────────────────────────────────────────────────────
//  CONTENIDO DEL MENÚ
//  Para añadir una práctica, añade un objeto en "items".
//  url: null  →  aparece como "Próximamente".
// ─────────────────────────────────────────────────────────────

export const categorias = [
  {
    nombre: 'Equipo',
    icono: 'equipo',
    items: [
      { titulo: 'David Molina', subtitulo: '', icono: 'persona', url: null, info: true },
      { titulo: 'Mario Luna', subtitulo: '', icono: 'persona', url: null, info: true },
      { titulo: 'Jose Antonio Nieto', subtitulo: '', icono: 'persona', url: null, info: true },
    ],
  },
  {
    nombre: 'UD1',
    icono: 'mando',
    items: [
      {
        titulo: 'Musicfy',
        subtitulo: 'App 1 · Recomendador musical con IA',
        icono: 'musica',
        url: 'https://proyectowebia.vercel.app/',
      },
      {
        titulo: 'Spec Kit',
        subtitulo: 'App 2 · Desarrollo guiado por especificaciones',
        icono: 'spec',
        url: 'https://musicfy-app2.vercel.app/',
      },
    ],
  },
  {
    nombre: 'UD2',
    icono: 'carpeta',
    items: [{ titulo: 'Próximamente', subtitulo: 'Nuevas prácticas', icono: 'carpeta', url: null }],
  },
]

// Categoría seleccionada al abrir la página (0 = Equipo, 1 = UD1…)
export const CATEGORIA_INICIAL = 1
