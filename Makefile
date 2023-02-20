.DEFAULT_GOAL := default

.PHONY: test logs

default: rebootd

start:
	docker compose up

stop:
	docker compose down -t 1

restart:
	docker compose restart

rebuild:
	docker compose build

rebuildf:
	docker compose build --no-cache

reboot: stop start

rebootd: stop startd logs

startd:
	docker compose up -d

top:
	docker compose top

ps:
	docker compose ps

logs:
	docker compose logs -f --tail 100

create-migration:
	cd src && pipenv run pw_migrate create --auto --auto-source 'models' --directory migrations --database sqlite:///../data/contacts.db $(n) && cd ..

apply-migration:
	cd src && pipenv run pw_migrate migrate --directory migrations --database sqlite:///../data/contacts.db && cd ..

apply-migration-name:
	cd src && pipenv run pw_migrate migrate --directory migrations --database sqlite:///../data/contacts.db --name $(n) && cd ..

test:
	pipenv run pytest -s -v --rootdir . --setup-show


export:
	export $(cat .env | sed 's/#.*//g' | xargs)
