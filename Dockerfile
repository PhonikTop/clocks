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


FROM python:3.12-alpine as api-prod

RUN apk add --no-cache libpq bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ /app

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "settings.asgi:application", "--host", "0.0.0.0",  "--port", "8000"]

FROM python:3.12-alpine as api-local

RUN apk add --no-cache libpq bash

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ /app

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "settings.asgi:application", "--reload", "--host", "0.0.0.0",  "--port", "8000"]
