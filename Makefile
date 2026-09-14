.PHONY: help setup up down logs seed migrate mobile-install android mobile check-api check-mobile test-domain smoke

help:
	@echo "setup | up | down | logs | seed | migrate | mobile-install | android | mobile | check-api | check-mobile | test-domain | smoke"

setup:
	python3 scripts/bootstrap.py

up:
	docker compose up --build -d --wait
	docker compose exec -T api python -m seekerlab.seed

down:
	docker compose down

logs:
	docker compose logs -f api

seed:
	docker compose exec -T api python -m seekerlab.seed

migrate:
	docker compose run --rm migrate

mobile-install:
	cd apps/mobile && if [ -f package-lock.json ]; then npm ci; else npm install; fi

android:
	cd apps/mobile && npm run android

mobile:
	cd apps/mobile && npm start

check-api:
	docker compose exec -T api python -m pytest -q

check-mobile:
	cd apps/mobile && npm run check

test-domain:
	PYTHONPATH=apps/api/src python3 -m unittest discover -s apps/api/tests/unit -v

smoke:
	python3 scripts/smoke.py
