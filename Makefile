.DEFAULT_GOAL := default

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

logs:
	docker compose logs -f

export:
	export $(cat .env | sed 's/#.*//g' | xargs)
