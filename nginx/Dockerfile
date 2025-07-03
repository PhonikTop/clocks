FROM node:18-alpine as frontend-builder
WORKDIR /app
COPY ./frontend/package.json ./frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
COPY .env.prod ./.env
RUN npm run lint --fix
RUN npm run build

FROM nginx:1.25-alpine

COPY --from=frontend-builder /app/dist /usr/share/nginx/html

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
