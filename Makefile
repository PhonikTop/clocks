begin: migrate collectstatic start

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

collectstatic:
	@docker-compose up -d watchy-db
	@docker-compose run --rm watchy-api python ./manage.py collectstatic

cli:
	@docker-compose run --rm watchy-api bash

createsuperuser:
	@docker-compose run --rm watchy-api python ./manage.py createsuperuser

tail:
	@docker-compose logs -f

faststart: clean build begin createsuperuser

.PHONY: start stop status restart clean build migrate collectstatic cli createsuperuser tail faststart