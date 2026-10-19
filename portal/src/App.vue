<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import FondoOndas from './components/FondoOndas.vue'
import Icono from './components/Icono.vue'
import { categorias, CATEGORIA_INICIAL } from './practicas.js'

// ---------- Estado del menú ----------
const cat = ref(CATEGORIA_INICIAL)
const seleccion = ref(categorias.map(() => 0)) // elemento elegido en cada categoría
const saliendo = ref(false)
const aviso = ref('')
let temporizadorAviso = null

const itemActual = computed(() => seleccion.value[cat.value])
const elemento = computed(() => categorias[cat.value].items[itemActual.value])

// ---------- Tamaño de pantalla (para colocar los iconos) ----------
const ancho = ref(window.innerWidth)
const alto = ref(window.innerHeight)
const escala = computed(() => Math.min(1.2, Math.max(0.6, Math.min(ancho.value / 1500, alto.value / 850))))
const filaY = computed(() => alto.value * 0.3)
const columnaX = computed(() => Math.max(ancho.value * 0.3, 70 * escala.value))
const separacionCat = computed(() => 190 * escala.value)

function posCategoria(i) {
  const x = columnaX.value + (i - cat.value) * separacionCat.value
  return { transform: `translate(${x}px, ${filaY.value}px) translate(-50%, -50%)` }
}

function posItem(i) {
  const e = escala.value
  const d = i - itemActual.value
  let y
  if (d < 0) y = filaY.value - 110 * e + (d + 1) * 80 * e // por encima de la fila
  else if (d === 0) y = filaY.value + 150 * e // el elegido, justo debajo
  else y = filaY.value + 150 * e + 125 * e + (d - 1) * 80 * e
  return { transform: `translate(${columnaX.value}px, ${y}px) translate(-${50 * e}px, -50%)` }
}

// ---------- Navegación ----------
function moverCategoria(paso) {
  const nuevo = cat.value + paso
  if (nuevo >= 0 && nuevo < categorias.length) cat.value = nuevo
}

function moverItem(paso) {
  const total = categorias[cat.value].items.length
  const nuevo = itemActual.value + paso
  if (nuevo >= 0 && nuevo < total) seleccion.value[cat.value] = nuevo
}

function mostrarAviso(texto) {
  aviso.value = texto
  clearTimeout(temporizadorAviso)
  temporizadorAviso = setTimeout(() => (aviso.value = ''), 2000)
}

function abrir() {
  const el = elemento.value
  if (el.info) return
  if (!el.url) return mostrarAviso('Disponible próximamente')
  saliendo.value = true
  setTimeout(() => (window.location.href = el.url), 450)
}

function clicCategoria(i) {
  cat.value = i
}

function clicItem(i) {
  if (i === itemActual.value) abrir()
  else seleccion.value[cat.value] = i
}

// Teclado
function alPulsar(e) {
  if (saliendo.value) return
  const acciones = {
    ArrowLeft: () => moverCategoria(-1),
    ArrowRight: () => moverCategoria(1),
    ArrowUp: () => moverItem(-1),
    ArrowDown: () => moverItem(1),
    Enter: abrir,
  }
  if (acciones[e.key]) {
    e.preventDefault()
    acciones[e.key]()
  }
}

// Rueda del ratón (con una pausa para no saltar varios de golpe)
let ultimaRueda = 0
function alRueda(e) {
  const ahora = Date.now()
  if (ahora - ultimaRueda < 180) return
  ultimaRueda = ahora
  if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) moverCategoria(Math.sign(e.deltaX))
  else moverItem(Math.sign(e.deltaY))
}

// Deslizar el dedo en móvil
let inicioToque = null
function alTocar(e) {
  inicioToque = { x: e.touches[0].clientX, y: e.touches[0].clientY }
}
function alSoltar(e) {
  if (!inicioToque) return
  const dx = e.changedTouches[0].clientX - inicioToque.x
  const dy = e.changedTouches[0].clientY - inicioToque.y
  inicioToque = null
  if (Math.max(Math.abs(dx), Math.abs(dy)) < 40) return
  if (Math.abs(dx) > Math.abs(dy)) moverCategoria(dx < 0 ? 1 : -1)
  else moverItem(dy < 0 ? 1 : -1)
}

function alRedimensionar() {
  ancho.value = window.innerWidth
  alto.value = window.innerHeight
}

// ---------- Reloj ----------
const ahora = ref(new Date())
let temporizadorReloj = null
const fecha = computed(() => `${ahora.value.getDate()}/${ahora.value.getMonth() + 1}`)
const hora = computed(() => ahora.value.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }))

onMounted(() => {
  window.addEventListener('keydown', alPulsar)
  window.addEventListener('resize', alRedimensionar)
  temporizadorReloj = setInterval(() => (ahora.value = new Date()), 10000)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', alPulsar)
  window.removeEventListener('resize', alRedimensionar)
  clearInterval(temporizadorReloj)
})
</script>

<template>
  <FondoOndas />

  <div class="fixed inset-0" @wheel.passive="alRueda" @touchstart.passive="alTocar" @touchend="alSoltar">
    <!-- Reloj -->
    <div
      class="absolute right-0 top-[7%] flex items-center justify-end gap-6 rounded-l-md border border-r-0 border-white/25 bg-white/10 py-2 pl-8 pr-6 sm:pr-10 backdrop-blur-sm"
      :style="{ minWidth: `${Math.min(ancho * 0.32, 520)}px` }"
    >
      <span class="text-2xl sm:text-3xl tracking-wide text-glow tabular-nums">{{ fecha }} {{ hora }}</span>
    </div>

    <!-- Fila de categorías (horizontal) -->
    <nav aria-label="Categorías">
      <button
        v-for="(c, i) in categorias"
        :key="c.nombre"
        type="button"
        class="absolute left-0 top-0 flex flex-col items-center transition-all duration-300 ease-out focus:outline-none"
        :class="i === cat ? 'opacity-100' : 'opacity-55 hover:opacity-80'"
        :style="posCategoria(i)"
        :aria-current="i === cat ? 'true' : undefined"
        @click="clicCategoria(i)"
      >
        <Icono
          :nombre="c.icono"
          class="glow transition-all duration-300"
          :style="{ width: `${(i === cat ? 96 : 68) * escala}px`, height: `${(i === cat ? 96 : 68) * escala}px` }"
        />
        <span
          class="mt-2 whitespace-nowrap text-glow transition-opacity duration-300"
          :class="i === cat ? 'opacity-100' : 'opacity-0'"
          :style="{ fontSize: `${22 * escala}px` }"
        >
          {{ c.nombre }}
        </span>
      </button>
    </nav>

    <!-- Elementos de la categoría elegida (vertical) -->
    <ul :key="cat" class="lista-entrada" :aria-label="categorias[cat].nombre">
      <li
        v-for="(item, i) in categorias[cat].items"
        :key="item.titulo"
        class="absolute left-0 top-0 transition-all duration-300 ease-out"
        :style="posItem(i)"
      >
        <button
          type="button"
          class="flex items-center text-left focus:outline-none"
          :class="i === itemActual ? 'opacity-100' : 'opacity-60 hover:opacity-85'"
          :aria-current="i === itemActual ? 'true' : undefined"
          @click="clicItem(i)"
        >
          <span
            class="grid place-items-center transition-all duration-300"
            :style="{ width: `${100 * escala}px`, height: `${(i === itemActual ? 100 : 64) * escala}px` }"
          >
            <Icono
              :nombre="item.icono"
              class="glow transition-all duration-300"
              :style="{ width: `${(i === itemActual ? 92 : 56) * escala}px`, height: `${(i === itemActual ? 92 : 56) * escala}px` }"
            />
          </span>
          <span class="ml-5 flex flex-col">
            <span
              class="whitespace-nowrap text-glow transition-all duration-300"
              :style="{ fontSize: `${(i === itemActual ? 34 : 20) * escala}px` }"
            >
              {{ item.titulo }}
            </span>
            <span
              v-if="i === itemActual"
              class="whitespace-nowrap text-white/85"
              :style="{ fontSize: `${17 * escala}px` }"
            >
              {{ aviso || item.subtitulo }}
            </span>
          </span>
        </button>
      </li>
    </ul>

    <!-- Ayuda de controles -->
    <p class="absolute bottom-4 right-6 text-sm text-white/60 hidden sm:block">
      ← → categoría &nbsp;·&nbsp; ↑ ↓ elegir &nbsp;·&nbsp; Enter abrir
    </p>
  </div>

  <!-- Fundido al abrir una práctica -->
  <div
    class="fixed inset-0 bg-black pointer-events-none transition-opacity duration-500"
    :class="saliendo ? 'opacity-100' : 'opacity-0'"
    aria-hidden="true"
  ></div>
</template>

<style scoped>
.lista-entrada {
  animation: aparecer 0.3s ease-out;
}
@keyframes aparecer {
  from { opacity: 0; }
  to { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .lista-entrada { animation: none; }
  * { transition: none !important; }
}
</style>
