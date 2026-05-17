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

RUN PYTHONPATH=/install/lib/python3.12/site-packages \
    python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' > /app/secret_key

FROM python:3.12-alpine AS api-prod

RUN apk add --no-cache libpq bash

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=settings.settings

COPY --from=builder /app/secret_key /app/secret_key
COPY --from=builder /install /usr/local
COPY . /app

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "settings.asgi:application", "--host", "0.0.0.0",  "--port", "8000"]

FROM python:3.12-alpine AS api-local

RUN apk add --no-cache libpq bash

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=settings.settings

COPY --from=builder /app/secret_key /app/secret_key
COPY --from=builder /install /usr/local
COPY . /app

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "settings.asgi:application", "--reload", "--host", "0.0.0.0",  "--port", "8000"]
