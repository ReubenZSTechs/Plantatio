# Plantatio web frontend: build the Vite bundle, serve it with nginx.
FROM node:22-alpine AS build

ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY deployment/nginx/spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
