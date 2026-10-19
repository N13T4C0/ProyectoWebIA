<script setup>
// Iconos propios (no son los de Sony): trazos blancos redondeados.
defineProps({ nombre: { type: String, required: true } })
</script>

<template>
  <svg
    viewBox="0 0 64 64"
    fill="none"
    stroke="currentColor"
    stroke-width="3.2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <!-- Mando genérico -->
    <template v-if="nombre === 'mando'">
      <path d="M18 22h28c7 0 11 6 12 14l1 8c1 6-6 9-10 4l-5-6H20l-5 6c-4 5-11 2-10-4l1-8c1-8 5-14 12-14z" fill="currentColor" fill-opacity=".9" />
      <path d="M18 30v8M14 34h8" stroke="#2a3f9e" />
      <circle cx="44" cy="31" r="1.8" fill="#2a3f9e" stroke="none" />
      <circle cx="49" cy="36" r="1.8" fill="#2a3f9e" stroke="none" />
    </template>

    <!-- Dos personas -->
    <template v-else-if="nombre === 'equipo'">
      <circle cx="24" cy="22" r="8" />
      <path d="M10 50c1-9 7-14 14-14s13 5 14 14" />
      <circle cx="43" cy="24" r="6.5" />
      <path d="M38 37c2-1 3.5-1.5 5-1.5 6 0 11 4.5 12 12.5" />
    </template>

    <!-- Una persona -->
    <template v-else-if="nombre === 'persona'">
      <circle cx="32" cy="22" r="9" />
      <path d="M14 52c1.5-10 9-16 18-16s16.5 6 18 16" />
    </template>

    <!-- Nota musical -->
    <template v-else-if="nombre === 'musica'">
      <path d="M26 44V14l24-5v30" />
      <ellipse cx="20" cy="44" rx="7" ry="5.5" fill="currentColor" />
      <ellipse cx="44" cy="39" rx="7" ry="5.5" fill="currentColor" />
      <path d="M26 22l24-5" />
    </template>

    <!-- Documento con lista (especificación) -->
    <template v-else-if="nombre === 'spec'">
      <path d="M16 8h24l10 10v38H16z" />
      <path d="M40 8v10h10" />
      <path d="M23 30l3 3 5-6M23 42l3 3 5-6M35 31h8M35 43h8" />
    </template>

    <!-- Carpeta -->
    <template v-else>
      <path d="M8 18c0-2 1.5-4 4-4h12l5 5h23c2.5 0 4 2 4 4v23c0 2-1.5 4-4 4H12c-2.5 0-4-2-4-4z" fill="currentColor" fill-opacity=".85" />
    </template>
  </svg>
</template>
