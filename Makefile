.PHONY: install dev docker-up docker-down docker-build \
        migrate fixtures seed reset \
        test test-unit test-app test-integration test-e2e lint

install:
	cp -n .env.example .env || true
	uv sync

dev:
	docker compose up -d db
	uv run uvicorn api.main:app --reload

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

migrate:
	uv run python -m django migrate --settings=config.django_settings

fixtures:
	uv run python scripts/generate_fixtures.py

seed:
	uv run python scripts/seed_db.py

reset:
	uv run python scripts/reset_db.py

test-unit:
	uv run pytest tests/unit/ -v

test-app:
	uv run pytest tests/application/ -v

test-integration:
	docker compose up -d db
	uv run pytest tests/integration/ -v

test-e2e:
	docker compose up -d db
	uv run pytest tests/e2e/ -v

test:
	uv run pytest tests/unit/ tests/application/ -v

lint:
	uv run ruff check src/ api/ tests/
