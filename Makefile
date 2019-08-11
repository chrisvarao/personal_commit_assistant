.PHONY: build up down test

build:
	docker-compose build

down:
	docker-compose down

up: build
	docker-compose up -d

test: up
	docker exec -ti `docker ps -q --filter="name=_test"` /bin/sh -c "python3 -m pytest tests/test.py"
