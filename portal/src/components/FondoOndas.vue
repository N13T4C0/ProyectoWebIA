<script setup>
// Fondo animado: degradado azul + una onda de luz formada por muchas líneas
// translúcidas + partículas brillantes. Todo dibujado en un <canvas> 2D.
import { ref, onMounted, onBeforeUnmount } from 'vue'

const lienzo = ref(null)
let ctx = null
let ancho = 0
let alto = 0
let dpr = 1
let animacion = null
let particulas = []
const reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches

const LINEAS = 18
const PARTICULAS = 140

// Altura de la onda en un punto x (0..1) para la línea k en el tiempo t
function ondaY(x, k, t) {
  const base = 0.62 - x * 0.2 // sube hacia la derecha
  const a = Math.sin(x * 3.1 + t * 0.35 + k * 0.09) * 0.05
  const b = Math.sin(x * 6.3 - t * 0.22 + k * 0.17) * 0.025
  const c = Math.sin(x * 1.4 + t * 0.12) * 0.04
  const separacion = (k - LINEAS / 2) * 0.006 * (1.1 + Math.sin(x * 2.5 + t * 0.3))
  return (base + a + b + c + separacion) * alto
}

function crearParticulas() {
  particulas = Array.from({ length: PARTICULAS }, () => ({
    x: Math.random(),
    desvio: (Math.random() - 0.5) * 0.25,
    vel: 0.004 + Math.random() * 0.012,
    tam: 0.6 + Math.random() * 1.6,
    fase: Math.random() * Math.PI * 2,
  }))
}

function ajustarTamano() {
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  ancho = window.innerWidth
  alto = window.innerHeight
  lienzo.value.width = ancho * dpr
  lienzo.value.height = alto * dpr
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
}

function dibujar(t) {
  // Degradado de fondo
  const fondo = ctx.createLinearGradient(0, 0, 0, alto)
  fondo.addColorStop(0, '#0f1846')
  fondo.addColorStop(0.55, '#1b2f8f')
  fondo.addColorStop(1, '#3555d8')
  ctx.globalCompositeOperation = 'source-over'
  ctx.fillStyle = fondo
  ctx.fillRect(0, 0, ancho, alto)

  // Resplandor bajo la onda
  const halo = ctx.createRadialGradient(ancho * 0.25, alto * 0.62, 0, ancho * 0.25, alto * 0.62, ancho * 0.6)
  halo.addColorStop(0, 'rgba(120,150,255,0.22)')
  halo.addColorStop(1, 'rgba(120,150,255,0)')
  ctx.fillStyle = halo
  ctx.fillRect(0, 0, ancho, alto)

  // Onda: una banda ancha y suave + muchas líneas finas sumando luz
  ctx.globalCompositeOperation = 'lighter'
  const paso = Math.max(8, ancho / 120)
  for (const [grosor, alfa] of [[90, 0.05], [45, 0.07]]) {
    ctx.beginPath()
    for (let px = -20; px <= ancho + 20; px += paso) {
      const y = ondaY(px / ancho, LINEAS / 2, t)
      if (px === -20) ctx.moveTo(px, y)
      else ctx.lineTo(px, y)
    }
    ctx.strokeStyle = `rgba(130,160,255,${alfa})`
    ctx.lineWidth = grosor * (alto / 900)
    ctx.stroke()
  }
  for (let k = 0; k < LINEAS; k++) {
    ctx.beginPath()
    for (let px = -20; px <= ancho + 20; px += paso) {
      const y = ondaY(px / ancho, k, t)
      if (px === -20) ctx.moveTo(px, y)
      else ctx.lineTo(px, y)
    }
    const central = 1 - Math.abs(k - LINEAS / 2) / (LINEAS / 2)
    ctx.strokeStyle = `rgba(150,175,255,${0.05 + central * 0.12})`
    ctx.lineWidth = 1 + central * 3
    ctx.stroke()
  }

  // Partículas que viajan a lo largo de la onda
  for (const p of particulas) {
    const x = ((p.x + t * p.vel) % 1.1) - 0.05
    const y = ondaY(x, LINEAS / 2, t) + p.desvio * alto * (0.3 + Math.abs(Math.sin(x * 3)))
    const brillo = 0.35 + 0.65 * Math.abs(Math.sin(t * 1.5 + p.fase))
    ctx.fillStyle = `rgba(220,230,255,${brillo * 0.8})`
    ctx.beginPath()
    ctx.arc(x * ancho, y, p.tam, 0, Math.PI * 2)
    ctx.fill()
  }
}

function bucle(ms) {
  dibujar(ms / 1000)
  animacion = requestAnimationFrame(bucle)
}

function alRedimensionar() {
  ajustarTamano()
  if (reducido) dibujar(0)
}

onMounted(() => {
  ctx = lienzo.value.getContext('2d')
  crearParticulas()
  ajustarTamano()
  window.addEventListener('resize', alRedimensionar)
  if (reducido) dibujar(0)
  else animacion = requestAnimationFrame(bucle)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animacion)
  window.removeEventListener('resize', alRedimensionar)
})
</script>

<template>
  <canvas ref="lienzo" class="fixed inset-0 w-full h-full -z-10" aria-hidden="true"></canvas>
</template>
