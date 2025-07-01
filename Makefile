begin: migrate collectstatic start

start:
	@docker compose up -d

stop:
	@docker compose stop

status:
	@docker compose ps

restart:
	@docker compose restart

clean: stop
ifndef KEEP_DB
	@docker compose rm --force watchy-db watchy-redis
endif
	@docker compose rm --force watchy-nginx watchy-api

build:
	@docker compose build

migrate:
ifndef SKIP_MIGRATE
	@docker compose up -d watchy-db
	@docker compose run --rm watchy-api python ./manage.py migrate
endif

collectstatic:
ifndef SKIP_COLLECTSTATIC
	@docker compose up -d watchy-db
	@docker compose run --rm watchy-api python ./manage.py collectstatic --noinput
endif

createsuperuser:
	@docker compose run --rm watchy-api python ./manage.py createsuperuser --noinput

tail:
	@docker compose logs -f

faststart: clean build collectstatic migrate start createsuperuser


.PHONY: start stop status restart clean build migrate collectstatic cli createsuperuser tail faststart