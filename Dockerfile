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

RUN tree

WORKDIR /Clocks/clocks
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

FROM py-builder AS watchy-api-local

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

CMD service nginx start && \
    uvicorn settings.asgi:application --reload --host 0.0.0.0 --port 8000

FROM py-builder AS watchy-api-prod

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

CMD service nginx start && \
    uvicorn settings.asgi:application --host 0.0.0.0 --port 8000
