# Makefile na raiz do projeto

.PHONY: dev api frontend down logs

dev:
	docker compose down --volumes
	docker compose build --no-cache
	docker compose up

api:
	docker compose up api --build

frontend:
	docker compose up frontend --build

down:
	docker compose down --volumes

logs:
	docker compose logs -f --tail=100
