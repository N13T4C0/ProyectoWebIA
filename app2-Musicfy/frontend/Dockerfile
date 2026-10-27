# Etapa 1: compilar el frontend. Solo entra la clave publishable de Clerk.
FROM node:22 AS build
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_URL=""
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2: Caddy sirve los estáticos, hace de proxy a la API y obtiene el certificado HTTPS.
FROM caddy:2
COPY --from=build /build/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
