begin: migrate start

start:
	@docker-compose up -d

stop:
	@docker-compose stop

status:
	@docker-compose ps

restart: stop start

clean: stop
	@docker-compose rm --force
	@find . -name \*.pyc -delete

build:
	@docker-compose build

migrate:
	@docker-compose up -d watchy-db
	@docker-compose run --rm watchy-api python ./manage.py migrate

cli:
	@docker-compose run --rm watchy-api bash

tail:
	@docker-compose logs -f

.PHONY: start stop status restart clean build migrate cli tail