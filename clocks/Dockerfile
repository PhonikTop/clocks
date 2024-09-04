# Базовый образ Python
FROM python:3.12-slim-bullseye as base

FROM base AS py-builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /clocks

RUN apt update -qq \
    && apt install -y -qq \
        make \
        nano \
        vim \
        nginx

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

FROM py-builder AS watchy-api-local

CMD service nginx start && \
    daphne -b 0.0.0.0 -p 8001 settings.asgi:application & \
    uvicorn settings.asgi:application --reload --host 0.0.0.0 --port 8000

FROM py-builder AS watchy-api-prod

COPY ../nginx/nginx.conf /etc/nginx/nginx.conf

CMD service nginx start && \
    daphne -b 0.0.0.0 -p 8001 settings.asgi:application & \
    uvicorn settings.asgi:application --host 0.0.0.0 --port 8000
