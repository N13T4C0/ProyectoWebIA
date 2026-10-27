<script setup>
import { ref, watch } from 'vue'
import { Show, SignInButton, UserButton, useAuth } from '@clerk/vue'
import { GENEROS, composeTastes, recommend } from './api.js'

const MENSAJE_VACIO = 'Elige algún género o escribe algo sobre la música que te gusta'
const MENSAJE_SIN_CONEXION = 'No se puede conectar con el servicio. Inténtalo más tarde.'

const { isSignedIn, getToken } = useAuth()

const seleccionados = ref([])
const texto = ref('')
const cargando = ref(false)
const resultado = ref('')
const error = ref('')
const sesionCaducada = ref(false)

// Al cerrar sesión no queda nada de la consulta anterior en pantalla (CA-RF04-04).
watch(isSignedIn, (conectado) => {
  if (conectado === false) {
    resultado.value = ''
    error.value = ''
    sesionCaducada.value = false
    cargando.value = false
  }
})

function alternarGenero(genero) {
  const i = seleccionados.value.indexOf(genero)
  if (i === -1) seleccionados.value.push(genero)
  else seleccionados.value.splice(i, 1)
}

async function enviar() {
  if (cargando.value || !isSignedIn.value) return
  // Los géneros se envían en el orden de la lista, no en el de selección.
  const tastes = composeTastes(
    GENEROS.filter((g) => seleccionados.value.includes(g)),
    texto.value,
  )
  sesionCaducada.value = false
  // Validación local: con el formulario vacío no se pide token ni se envía nada (CA-RF01-04).
  if (tastes === '') {
    error.value = MENSAJE_VACIO
    return
  }
  error.value = ''
  cargando.value = true
  try {
    const token = await getToken.value()
    const { status, data } = await recommend(tastes, token)
    // Si se cerró sesión mientras esperaba, la respuesta ya no se muestra.
    if (!isSignedIn.value) return
    if (status === 200) {
      resultado.value = data.resultado
    } else {
      // Sin conexión o sin cuerpo de error del contrato: mensaje genérico.
      error.value = data?.error?.mensaje ?? MENSAJE_SIN_CONEXION
      sesionCaducada.value = status === 401
    }
  } catch {
    error.value = MENSAJE_SIN_CONEXION
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <main class="mx-auto flex max-w-xl flex-col gap-6 px-4 py-8">
    <header class="flex items-center justify-between gap-4">
      <h1 class="text-3xl font-bold">Musicfy</h1>
      <Show when="signed-out">
        <SignInButton mode="modal">
          <button type="button" class="rounded border border-indigo-600 px-4 py-2 font-medium text-indigo-700">
            Iniciar sesión
          </button>
        </SignInButton>
      </Show>
      <Show when="signed-in">
        <UserButton />
      </Show>
    </header>

    <form class="flex flex-col gap-4" @submit.prevent="enviar">
      <div role="group" aria-label="Géneros musicales" class="flex flex-wrap gap-2">
        <button
          v-for="genero in GENEROS"
          :key="genero"
          type="button"
          :aria-pressed="seleccionados.includes(genero)"
          class="rounded-full border px-3 py-1 text-sm"
          :class="
            seleccionados.includes(genero)
              ? 'border-indigo-600 bg-indigo-600 text-white'
              : 'border-gray-300 bg-white text-gray-800'
          "
          @click="alternarGenero(genero)"
        >
          <span v-if="seleccionados.includes(genero)" aria-hidden="true">✓ </span>{{ genero }}
        </button>
      </div>

      <div class="flex flex-col gap-1">
        <label for="gustos" class="font-medium">¿Qué música te gusta?</label>
        <textarea
          id="gustos"
          v-model="texto"
          rows="4"
          class="w-full rounded border border-gray-300 p-2"
        ></textarea>
      </div>

      <button
        type="submit"
        :disabled="!isSignedIn || cargando"
        class="self-start rounded bg-indigo-600 px-4 py-2 font-medium text-white disabled:opacity-50"
      >
        Recomendar
      </button>
    </form>

    <p aria-live="polite" class="text-gray-600">
      <span v-if="cargando">Buscando recomendaciones…</span>
    </p>

    <p v-if="error" class="break-words text-red-700">
      {{ error }}
      <template v-if="sesionCaducada"> Inicia sesión de nuevo para continuar.</template>
    </p>

    <!-- Interpolación de texto, nunca v-html; el contenido va en línea por whitespace-pre-line. -->
    <section
      v-if="resultado"
      class="whitespace-pre-line break-words rounded border border-gray-200 p-4"
    >{{ resultado }}</section>
  </main>
</template>
