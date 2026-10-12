<script setup>
// Título con efecto de pantalla CRT:
// 1) el texto se dibuja en un canvas 2D,
// 2) ese canvas se usa como textura en WebGL,
// 3) un shader le aplica temblor por líneas, aberración cromática,
//    máscara RGB, líneas de barrido, grano y "glitches" ocasionales.
// El texto real está en el <h1> (oculto visualmente) para lectores de pantalla.
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  // [{ texto: '...', cursiva: false }, ...]
  lineas: { type: Array, required: true },
  color: { type: String, default: '#f58cf5' },
})

const contenedor = ref(null)
const lienzo = ref(null)
const sinWebGL = ref(false)

const textoCanvas = document.createElement('canvas')
let gl = null
let programa = null
let textura = null
let uniformes = {}
let observador = null
let animacion = null
let inicio = 0
let proximoGlitch = 0
let glitchHasta = 0
let fuerzaGlitch = 0
let movimientoReducido = false

const VERTEX = `
attribute vec2 aPos;
varying vec2 vUv;
void main() {
  vUv = vec2(aPos.x * 0.5 + 0.5, 0.5 - aPos.y * 0.5);
  gl_Position = vec4(aPos, 0.0, 1.0);
}`

const FRAGMENT = `
precision highp float;
uniform sampler2D tMap;
uniform vec2 uRes;
uniform float uTime;
uniform float uGlitch;
uniform float uDpr;
uniform vec3 uFondo;
varying vec2 vUv;

float rand(float n) { return fract(sin(n * 12.9898) * 43758.5453); }
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

void main() {
  vec2 uv = vUv;

  // Temblor horizontal por líneas (siempre un poco, mucho durante un glitch)
  float fila = floor(uv.y * uRes.y / (2.0 * uDpr));
  float salto = floor(uTime * 24.0);
  uv.x += (rand(fila + salto) - 0.5) * (1.2 * uDpr / uRes.x + uGlitch * 0.03);

  // Bandas desplazadas durante el glitch
  float banda = step(0.82, rand(floor(uv.y * 9.0) + salto * 1.7));
  uv.x += banda * uGlitch * (rand(salto) - 0.5) * 0.12;

  // Aberración cromática radial: rojo hacia fuera, azul hacia dentro
  vec2 dir = normalize(uv - 0.5 + 0.0001);
  vec2 ca = dir * (1.5 + uGlitch * 7.0) * uDpr / uRes;
  float r = texture2D(tMap, uv + ca).r;
  float g = texture2D(tMap, uv).g;
  float b = texture2D(tMap, uv - ca).b;
  vec3 col = vec3(r, g, b);

  // Máscara de subpíxeles RGB de un monitor antiguo
  float pp = mod(floor(gl_FragCoord.x / max(1.0, uDpr * 0.75)), 3.0);
  vec3 mascara = vec3(0.15);
  if (pp < 0.5) mascara.r = 1.0; else if (pp < 1.5) mascara.g = 1.0; else mascara.b = 1.0;
  col = mix(col, col * mascara * 1.3, 0.2);

  // Líneas de barrido
  float linea = step(1.0, mod(gl_FragCoord.y, 2.0 * uDpr + 1.0));
  col *= mix(0.72, 1.0, linea);

  // Grano solo sobre el texto, para que el fondo siga totalmente negro
  col += (hash(gl_FragCoord.xy + uTime * 60.0) - 0.5) * 0.12;

  // Los efectos solo se aplican donde hay texto; el resto queda del color del fondo
  vec3 original = vec3(r, g, b);
  float esTexto = smoothstep(0.03, 0.15, distance(original, uFondo));
  col = mix(uFondo, col, esTexto);

  gl_FragColor = vec4(max(col, 0.0), 1.0);
}`

function crearShader(tipo, codigo) {
  const s = gl.createShader(tipo)
  gl.shaderSource(s, codigo)
  gl.compileShader(s)
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s))
  return s
}

function iniciarWebGL() {
  gl = lienzo.value.getContext('webgl', { antialias: false, premultipliedAlpha: false })
  if (!gl) throw new Error('WebGL no disponible')

  programa = gl.createProgram()
  gl.attachShader(programa, crearShader(gl.VERTEX_SHADER, VERTEX))
  gl.attachShader(programa, crearShader(gl.FRAGMENT_SHADER, FRAGMENT))
  gl.linkProgram(programa)
  if (!gl.getProgramParameter(programa, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(programa))
  gl.useProgram(programa)

  // Un rectángulo que ocupa todo el canvas
  const buffer = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW)
  const aPos = gl.getAttribLocation(programa, 'aPos')
  gl.enableVertexAttribArray(aPos)
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0)

  textura = gl.createTexture()
  gl.bindTexture(gl.TEXTURE_2D, textura)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)

  for (const nombre of ['tMap', 'uRes', 'uTime', 'uGlitch', 'uDpr', 'uFondo']) {
    uniformes[nombre] = gl.getUniformLocation(programa, nombre)
  }
}

// Parte una línea en varias si no cabe en el ancho disponible
function partirLinea(ctx, texto, anchoMax) {
  const palabras = texto.split(' ')
  const resultado = []
  let actual = ''
  for (const palabra of palabras) {
    const prueba = actual ? `${actual} ${palabra}` : palabra
    if (ctx.measureText(prueba).width > anchoMax && actual) {
      resultado.push(actual)
      actual = palabra
    } else {
      actual = prueba
    }
  }
  if (actual) resultado.push(actual)
  return resultado
}

// Color de fondo real de la página (así el canvas no se ve como un rectángulo)
function colorFondo() {
  return getComputedStyle(document.body).backgroundColor // "rgb(r, g, b)"
}

function dibujarTexto() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const anchoCss = contenedor.value.clientWidth
  const tamano = Math.max(24, Math.min(42, anchoCss * 0.04))
  const interlineado = tamano * 1.05
  const margen = 14

  const ctx = textoCanvas.getContext('2d')
  const fuente = (cursiva) => `${cursiva ? 'italic ' : ''}400 ${tamano * dpr}px "Instrument Serif", Georgia, serif`

  // Calcula las líneas finales (con saltos automáticos en pantallas estrechas)
  const filas = []
  for (const linea of props.lineas) {
    ctx.font = fuente(linea.cursiva)
    for (const trozo of partirLinea(ctx, linea.texto, (anchoCss - margen * 2) * dpr)) {
      filas.push({ texto: trozo, cursiva: linea.cursiva })
    }
  }

  const altoCss = Math.ceil(filas.length * interlineado + margen * 2)
  textoCanvas.width = Math.round(anchoCss * dpr)
  textoCanvas.height = Math.round(altoCss * dpr)

  ctx.fillStyle = colorFondo()
  ctx.fillRect(0, 0, textoCanvas.width, textoCanvas.height)
  ctx.fillStyle = props.color
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  filas.forEach((fila, i) => {
    ctx.font = fuente(fila.cursiva)
    ctx.fillText(fila.texto, textoCanvas.width / 2, (margen + interlineado * (i + 0.5)) * dpr)
  })

  const c = lienzo.value
  c.width = textoCanvas.width
  c.height = textoCanvas.height
  c.style.height = `${altoCss}px`

  gl.viewport(0, 0, c.width, c.height)
  gl.bindTexture(gl.TEXTURE_2D, textura)
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, textoCanvas)
  gl.uniform1i(uniformes.tMap, 0)
  gl.uniform2f(uniformes.uRes, c.width, c.height)
  gl.uniform1f(uniformes.uDpr, dpr)
  const [r, g, b] = colorFondo().match(/\d+/g).map(Number)
  gl.uniform3f(uniformes.uFondo, r / 255, g / 255, b / 255)
}

function pintar(tiempo, glitch) {
  gl.uniform1f(uniformes.uTime, tiempo / 1000)
  gl.uniform1f(uniformes.uGlitch, glitch)
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
}

function bucle(ahora) {
  // Entrada: empieza muy distorsionado y se estabiliza en ~0,9 s
  const entrada = Math.min(1, Math.max(0, 1 - (ahora - inicio) / 900))

  // Glitch breve cada 2,5-6,5 s
  if (ahora > proximoGlitch) {
    fuerzaGlitch = 0.35 + Math.random() * 0.6
    glitchHasta = ahora + 100 + Math.random() * 180
    proximoGlitch = ahora + 2500 + Math.random() * 4000
  }
  const glitch = Math.max(entrada, ahora < glitchHasta ? fuerzaGlitch : 0)

  pintar(ahora, glitch)
  animacion = requestAnimationFrame(bucle)
}

onMounted(async () => {
  movimientoReducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  try {
    iniciarWebGL()
  } catch {
    sinWebGL.value = true // se muestra el título normal con CSS
    return
  }

  // Espera a que carguen las fuentes para no dibujar con la de reserva
  await Promise.all([
    document.fonts.load('400 40px "Instrument Serif"'),
    document.fonts.load('italic 400 40px "Instrument Serif"'),
  ]).catch(() => {})

  dibujarTexto()
  observador = new ResizeObserver(() => {
    dibujarTexto()
    if (movimientoReducido) pintar(0, 0)
  })
  observador.observe(contenedor.value)

  if (movimientoReducido) {
    pintar(0, 0) // imagen fija, sin animación
  } else {
    inicio = performance.now() + 700 // empieza cuando la "tele" ya está encendida
    proximoGlitch = inicio + 2500
    animacion = requestAnimationFrame(bucle)
  }
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animacion)
  observador?.disconnect()
})
</script>

<template>
  <h1>
    <span
      :class="sinWebGL
        ? 'block font-display chroma text-neon text-center text-4xl sm:text-5xl md:text-6xl leading-[1.05]'
        : 'sr-only'"
    >
      <template v-for="(linea, i) in lineas" :key="i">
        <em v-if="linea.cursiva" class="block">{{ linea.texto }}</em>
        <span v-else class="block">{{ linea.texto }}</span>
      </template>
    </span>
    <div v-show="!sinWebGL" ref="contenedor" aria-hidden="true">
      <canvas ref="lienzo" class="block w-full"></canvas>
    </div>
  </h1>
</template>
