FROM python:3.12-alpine AS builder

RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        libffi-dev \
        postgresql-dev \
        cargo \
        python3-dev \
    && apk add --no-cache bash

WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-alpine AS test-builder

RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        libffi-dev \
        postgresql-dev \
        cargo \
        python3-dev \
    && apk add --no-cache bash

WORKDIR /app


COPY requirements-tests.txt requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements-tests.txt


FROM python:3.12-alpine as api-prod

RUN apk add --no-cache libpq bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY clocks/ /app

ENTRYPOINT ["uvicorn", "settings.asgi:application", "--host", "0.0.0.0",  "--port", "8000"]

FROM python:3.12-alpine as api-local

RUN apk add --no-cache libpq bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY clocks/ /app

CMD ["uvicorn", "settings.asgi:application", "--reload", "--host", "0.0.0.0",  "--port", "8000"]


FROM python:3.12-alpine as api-test

RUN apk add --no-cache libpq bash

COPY --from=test-builder /install /usr/local
COPY clocks/ /app

WORKDIR /app

RUN find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -r {} +

CMD ["pytest", "/app/clocks"]
