# Etapa 1: compila Angular.
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2: nginx sirve los archivos compilados y reenvía /api al backend.
# La imagen "unprivileged" corre nginx sin root y escucha en el puerto 8080.
FROM nginxinc/nginx-unprivileged:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/conciliador-frontend/browser /usr/share/nginx/html
EXPOSE 8080
