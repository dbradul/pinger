start:
	docker-compose up

stop:
	docker-compose down

restart:
	docker-compose restart

rebuild:
	docker-compose build

rebuildf:
	docker-compose build --no-cache

reboot:
	docker-compose down && docker-compose up

startd:
	docker-compose up -d

rebootd:
	docker-compose down && docker-compose up -d

logs:
	docker-compose logs -f

top:
	docker-compose top

export:
	export $(cat .env | sed 's/#.*//g' | xargs)
