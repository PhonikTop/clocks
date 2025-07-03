ENV ?= dev

COMPOSE_FILE = docker-compose.$(ENV).yml

CHECK_COMPOSE_FILE:
	@if [ ! -f "$(COMPOSE_FILE)" ]; then \
		echo "Error: $(COMPOSE_FILE) not found"; \
		exit 1; \
	fi

start: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) up -d

stop: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) stop

status: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) ps

restart: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) restart

clean: CHECK_COMPOSE_FILE stop
ifndef KEEP_DB
	@docker compose -f $(COMPOSE_FILE) rm --force watchy-db watchy-redis
endif
	@docker compose -f $(COMPOSE_FILE) rm --force watchy-nginx watchy-api

build: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) build

migrate: CHECK_COMPOSE_FILE
ifndef SKIP_MIGRATE
	@docker compose -f $(COMPOSE_FILE) up -d watchy-db
	@docker compose -f $(COMPOSE_FILE) run --rm watchy-api python ./manage.py migrate
endif

collectstatic: CHECK_COMPOSE_FILE
ifndef SKIP_COLLECTSTATIC
	@docker compose -f $(COMPOSE_FILE) up -d watchy-db
	@docker compose -f $(COMPOSE_FILE) run --rm watchy-api python ./manage.py collectstatic --noinput
endif

createsuperuser: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) run --rm watchy-api python ./manage.py createsuperuser --noinput

tail: CHECK_COMPOSE_FILE
	@docker compose -f $(COMPOSE_FILE) logs -f

faststart: CHECK_COMPOSE_FILE clean build collectstatic migrate start createsuperuser

.PHONY: start stop status restart clean build migrate collectstatic createsuperuser tail faststart CHECK_COMPOSE_FILE