<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// Cada cuánto se repite la animación (ms) y en qué segundo se queda quieto el logo
const INTERVALO_MS = 8000
const FOTOGRAMA_REPOSO = 0
const RETRASO_INICIAL_MS = 1600 // espera a que termine la entrada de la página

const video = ref(null)
let temporizador = null

function reproducir() {
  video.value?.play().catch(() => {}) // si el navegador bloquea el autoplay, se queda el póster
}

function alTerminar() {
  video.value.pause()
  video.value.currentTime = FOTOGRAMA_REPOSO
  temporizador = setTimeout(reproducir, INTERVALO_MS)
}

onMounted(() => {
  // Si el usuario pide reducir animaciones, solo se muestra la imagen fija
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  temporizador = setTimeout(reproducir, RETRASO_INICIAL_MS)
})

onBeforeUnmount(() => clearTimeout(temporizador))
</script>

<template>
  <div role="img" aria-label="Musicfy" class="logo-entrada inline-block mix-blend-screen">
    <video
      ref="video"
      poster="/logo-poster.jpg"
      muted
      playsinline
      preload="auto"
      aria-hidden="true"
      class="h-20 sm:h-24 w-auto select-none pointer-events-none"
      @ended="alTerminar"
    >
      <source src="/logo.webm" type="video/webm" />
      <source src="/logo.mp4" type="video/mp4" />
    </video>
  </div>
</template>
