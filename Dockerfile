# Базовый образ Python
FROM python:3.12-slim-bullseye as base

FROM base AS py-builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /Clocks

RUN apt update -qq \
    && apt install -y -qq \
        make \
        nano \
        vim \
        nginx \
        tree

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /Clocks/clocks
