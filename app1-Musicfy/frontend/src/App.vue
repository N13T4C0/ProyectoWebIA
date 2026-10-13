<script setup>
import { ref, computed } from 'vue'
import { recomendar, MAX_CARACTERES } from './api.js'
import { resaltarArtistas } from './resaltarArtistas.js'
import LogoAnimado from './components/LogoAnimado.vue'
import TituloCRT from './components/TituloCRT.vue'

const titulo = [
  { texto: 'Cuéntanos qué música te mueve', cursiva: false },
  { texto: 'y descubre a quién escuchar después.', cursiva: true },
]

const ejemplos = [
  'Indie 2000s · Arctic Monkeys',
  'Flamenco fusión · Rosalía',
  'Electrónica chill · Bonobo',
]

const GENEROS = [
  'Indie', 'Rock', 'Pop', 'Electrónica', 'Hip hop', 'Flamenco',
  'Jazz', 'Metal', 'R&B', 'Reggaetón', 'Clásica', 'Lo-fi',
]
const MAX_GENEROS = 5

// Línea blanca del encendido de tele (se quita al terminar la animación)
const mostrarEncendido = ref(true)

const gustos = ref('')
const generosElegidos = ref([])
const estado = ref('inicial') // 'inicial' | 'cargando' | 'resultado' | 'error'
const resultado = ref('')
const mensajeError = ref('')
const errorValidacion = ref('')

// Texto que se envía al backend: géneros elegidos + lo que haya escrito el usuario
const textoEnviar = computed(() => {
  const texto = gustos.value.trim()
  if (!generosElegidos.value.length) return texto
  const generos = `Géneros: ${generosElegidos.value.join(', ').toLowerCase()}.`
  return texto ? `${generos} Además: ${texto}` : generos
})

const caracteres = computed(() => textoEnviar.value.length)
const excedido = computed(() => caracteres.value > MAX_CARACTERES)
const cargando = computed(() => estado.value === 'cargando')
const limiteGeneros = computed(() => generosElegidos.value.length >= MAX_GENEROS)
const lineasResultado = computed(() => resaltarArtistas(resultado.value))

function alternarGenero(genero) {
  const i = generosElegidos.value.indexOf(genero)
  if (i !== -1) generosElegidos.value.splice(i, 1)
  else if (!limiteGeneros.value) generosElegidos.value.push(genero)
  errorValidacion.value = ''
}

function validar() {
  if (!textoEnviar.value) return 'Elige algún género o escribe algo sobre la música que te gusta.'
  if (excedido.value) return `El texto no puede superar los ${MAX_CARACTERES} caracteres.`
  return ''
}

async function enviar() {
  if (cargando.value) return // evita envíos duplicados

  errorValidacion.value = validar()
  if (errorValidacion.value) return

  estado.value = 'cargando'
  resultado.value = ''
  mensajeError.value = ''

  try {
    const data = await recomendar(textoEnviar.value)
    resultado.value = data.resultado
    estado.value = 'resultado'
  } catch (e) {
    mensajeError.value = e.mensaje ?? 'Algo ha fallado. Inténtalo de nuevo.'
    estado.value = 'error'
  }
}

function usarEjemplo(texto) {
  gustos.value = texto
  errorValidacion.value = ''
}
</script>

<template>
  <div
    v-if="mostrarEncendido"
    class="tv-linea"
    aria-hidden="true"
    @animationend="mostrarEncendido = false"
  ></div>

  <div class="tv-contenido bg-ink min-h-dvh flex flex-col">
    <!-- Barra superior -->
    <div class="h-2 mx-3 mt-3 bg-neon chroma-box" aria-hidden="true"></div>

    <!-- Cabecera con el logo animado -->
    <header class="px-4 sm:px-6 pt-3 flex justify-center">
      <LogoAnimado />
    </header>

    <main class="flex-1 w-full max-w-5xl mx-auto px-4 pb-12">
      <TituloCRT :lineas="titulo" class="mt-1" />

      <form class="max-w-3xl mx-auto mt-3 sm:mt-4" novalidate @submit.prevent="enviar">
        <label
          for="gustos"
          class="block text-center uppercase tracking-widest text-xl sm:text-2xl text-neon chroma mb-3"
        >
          <span aria-hidden="true"></span>Tus gustos musicales<span aria-hidden="true"></span>
        </label>

        <div class="bg-tarjeta border border-white/10 rounded-2xl shadow-lg shadow-black/20 p-4 sm:p-6">
          <!-- Géneros: se pueden marcar varios (hasta MAX_GENEROS) -->
          <fieldset class="mb-3">
            <legend class="mb-2 flex w-full items-baseline justify-between gap-4 text-lg">
              <span class="uppercase text-neutral-400">Elige géneros</span>
              <span class="tabular-nums text-neutral-500">{{ generosElegidos.length }}/{{ MAX_GENEROS }}</span>
            </legend>
            <div class="flex flex-wrap gap-2 text-lg sm:text-xl">
              <button
                v-for="genero in GENEROS"
                :key="genero"
                type="button"
                :aria-pressed="generosElegidos.includes(genero) ? 'true' : 'false'"
                :disabled="cargando || (limiteGeneros && !generosElegidos.includes(genero))"
                class="rounded-full border px-3 leading-8 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-neon/40 disabled:opacity-40 disabled:cursor-not-allowed"
                :class="generosElegidos.includes(genero)
                  ? 'bg-neon text-ink border-neon chroma-box'
                  : 'bg-white/5 border-white/10 text-neutral-300 hover:bg-white/10 hover:text-white'"
                @click="alternarGenero(genero)"
              >
                {{ genero }}
              </button>
            </div>
          </fieldset>

          <textarea
            id="gustos"
            v-model="gustos"
            rows="3"
            :disabled="cargando"
            :aria-invalid="errorValidacion ? 'true' : 'false'"
            aria-describedby="ayuda-gustos contador-gustos error-gustos"
            placeholder="Ej.: me flipa el indie de los 2000, algo de shoegaze y Rosalía cuando estoy de bajón…"
            class="w-full resize-y bg-ink/70 border border-white/10 rounded-xl p-3 text-xl leading-snug text-neutral-100 placeholder:text-neutral-500 transition-colors focus:outline-none focus-visible:border-neon/70 focus-visible:ring-2 focus-visible:ring-neon/20 disabled:opacity-60"
            @input="errorValidacion = ''"
          ></textarea>

          <div class="mt-1 flex items-start justify-between gap-4 text-lg">
            <p id="ayuda-gustos" class="text-neutral-500">Artistas, géneros, épocas, momentos…</p>
            <p
              id="contador-gustos"
              class="shrink-0 tabular-nums"
              :class="excedido ? 'text-red-400' : 'text-neutral-500'"
            >
              {{ caracteres }}/{{ MAX_CARACTERES }}
            </p>
          </div>

          <p v-if="errorValidacion" id="error-gustos" role="alert" class="text-red-400 text-xl">{{ errorValidacion }}</p>

          <!-- Ejemplos para rellenar el campo -->
          <div class="mt-2 flex flex-wrap items-center gap-2 text-base sm:text-lg">
            <span class="text-neutral-500 uppercase">Prueba con:</span>
            <button
              v-for="ejemplo in ejemplos"
              :key="ejemplo"
              type="button"
              :disabled="cargando"
              class="rounded-full bg-white/5 border border-white/10 px-3 leading-7 text-neutral-300 transition-colors hover:bg-white/10 hover:text-white focus:outline-none focus-visible:border-neon/70 disabled:opacity-50"
              @click="usarEjemplo(ejemplo)"
            >
              {{ ejemplo }}
            </button>
          </div>

          <div class="mt-4 flex justify-center">
            <button
              type="submit"
              :disabled="cargando"
              class="w-full sm:w-auto rounded-xl bg-neutral-100 text-ink uppercase tracking-wider text-2xl px-10 py-1.5 transition-colors hover:bg-white focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-4 focus-visible:ring-offset-ink focus-visible:ring-neon disabled:opacity-60 disabled:cursor-wait"
            >
              {{ cargando ? 'Buscando…' : 'Recomiéndame artistas' }}
            </button>
          </div>
        </div>
      </form>

      <!-- Zona de resultado: espera, resultado o error -->
      <section class="max-w-3xl mx-auto mt-8" aria-live="polite">
        <p v-if="estado === 'cargando'" class="text-center text-2xl uppercase tracking-widest text-neutral-400">
          Buscando artistas para ti
          <span class="inline-block animate-pulse motion-reduce:animate-none" aria-hidden="true">▌</span>
        </p>

        <div v-else-if="estado === 'resultado'" class="bg-tarjeta border border-white/10 rounded-2xl shadow-lg shadow-black/20 p-4 sm:p-6">
          <h2 class="uppercase tracking-widest text-xl text-neutral-400 mb-2">
            <span aria-hidden="true">✦ </span>Tus recomendaciones
          </h2>
          <!-- Se muestra como texto plano: nunca v-html con contenido de la IA -->
          <p class="whitespace-pre-wrap break-words text-xl leading-snug text-neutral-100"><template
              v-for="(linea, i) in lineasResultado"
              :key="i"
            ><template v-for="(t, j) in linea" :key="j"><strong
                  v-if="t.artista"
                  class="font-normal text-2xl text-neon chroma"
                >{{ t.texto }}</strong><template v-else>{{ t.texto }}</template></template>{{ i < lineasResultado.length - 1 ? '\n' : '' }}</template></p>
        </div>

        <div v-else-if="estado === 'error'" role="alert" class="bg-red-950/40 border border-red-500/40 rounded-2xl p-4 sm:p-6">
          <h2 class="uppercase tracking-widest text-xl text-red-400 mb-1">
            <span aria-hidden="true">✱ </span>Algo ha fallado
          </h2>
          <p class="text-xl text-red-200">{{ mensajeError }}</p>
        </div>
      </section>
    </main>
  </div>
</template>
