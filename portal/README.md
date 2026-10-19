# Portal de prácticas

> **Este portal no forma parte de la entrega de la PR01-UD1.** Es un menú personal del equipo,
> inspirado en la interfaz de la PS3, para acceder a las demos desplegadas de cada práctica.
> Musicfy sigue siendo una aplicación de una sola pantalla, independiente de este menú.

## Estructura

```text
ProyectoWebIA/
├── app1-Musicfy/        ← práctica (App 1)
├── vercel.json          ← despliegue de Musicfy
└── portal/              ← este menú (proyecto aparte)
    └── src/
        ├── practicas.js ← AQUÍ se añaden prácticas y sus URLs
        ├── App.vue      ← navegación del menú
        └── components/  ← fondo de ondas e iconos propios
```

## Arrancar en local

```bash
cd portal
npm install
npm run dev -- --port 5180
```

Uso el puerto 5180 para no chocar con el frontend de Musicfy (5173).

## Añadir una práctica

En `src/practicas.js`, añade un elemento con `titulo`, `subtitulo`, `icono` y `url`
(la URL pública de su demo). Con `url: null` aparece como «Disponible próximamente».

## Controles

- ← → cambiar de categoría · ↑ ↓ elegir · Enter abrir
- Ratón: clic para elegir, clic otra vez para abrir; rueda para subir/bajar
- Móvil: deslizar el dedo

## Desplegar en Vercel

Proyecto de Vercel **distinto** al de Musicfy, con *Root Directory* `portal`,
framework Vite y salida `dist`.

## Créditos

El fondo de ondas y los iconos están dibujados por código; no se usan imágenes ni logotipos de Sony.
