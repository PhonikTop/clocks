FROM python:3.12-slim-bullseye as base

# в этом образе устанавливаем и собираем пакеты
FROM base AS py-builder

WORKDIR code

RUN apt update -qq \
    && apt install -y -qq \
        make \
        nano \
        vim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM py-builder AS watchy-api-local

ENTRYPOINT ["uvicorn", "settings.asgi:application", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM py-builder AS api-prod

ENTRYPOINT ["uvicorn", "settings.asgi:application", "--reload", "--host", "0.0.0.0", "--port", "8000"]
