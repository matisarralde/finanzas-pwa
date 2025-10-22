# apps/backend/Makefile

.PHONY: install dev migrate seed test ingest clean

install:
	poetry install

dev:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	poetry run alembic upgrade head

migrate-create:
	poetry run alembic revision --autogenerate -m "$(message)"

seed:
	poetry run python scripts/seed.py

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src --cov-report=html

ingest:
	@echo "Run manual ingestion via POST /gmail/ingest/run with credentials"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

format:
	poetry run black src/
	poetry run ruff --fix src/

docker-build:
	docker build -t finance-api .

docker-run:
	docker run -p 8000:8000 --env-file .env finance-api
