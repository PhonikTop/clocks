# Stage 1: builder
FROM python:3.12-alpine AS builder

# Устанавливаем зависимости для сборки пакетов
RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        libffi-dev \
        postgresql-dev \
        cargo \
        python3-dev \
    && apk add --no-cache bash

WORKDIR /app


# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости в отдельный каталог
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: final
FROM python:3.12-alpine

# Минимальные зависимости для работы Python
RUN apk add --no-cache libpq bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY clocks/ /app

WORKDIR /app
