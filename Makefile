begin: migrate collectstatic start

start:
	@docker-compose up -d

stop:
	@docker-compose stop

status:
	@docker-compose ps

restart: stop start

clean: stop
ifndef NO_DB_RESET
	@docker-compose rm --force watchy-db watchy-redis
endif
	@docker-compose rm --force watchy-nginx watchy-api
	@find . -name \*.pyc -delete

build:
	@docker-compose build

migrate:
ifndef NO_DB_RESET
	@docker-compose up -d watchy-db
	@docker-compose run --rm watchy-api python ./manage.py migrate
endif

collectstatic:
ifndef NO_COLLECTSTATIC
	@docker-compose up -d watchy-db
	@docker-compose run --rm watchy-api python ./manage.py collectstatic
endif

cli:
	@docker-compose run --rm watchy-api bash

createsuperuser:
	@docker-compose run --rm watchy-api python ./manage.py createsuperuser

tail:
	@docker-compose logs -f

faststart: clean build begin createsuperuser

deploy:
	@$(MAKE) clean NO_DB_RESET=1
	@$(MAKE) build
	@$(MAKE) begin NO_DB_RESET=1

.PHONY: start stop status restart clean build migrate collectstatic cli createsuperuser tail faststart deploy