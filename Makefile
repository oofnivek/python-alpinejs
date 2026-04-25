.PHONY: install dev test test-cov lint migrate seed

# ── Setup ─────────────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

# ── Dev server ────────────────────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	pytest -x

test-cov:
	pytest --cov=app --cov-report=html:htmlcov --cov-report=term-missing
	@echo "\n✅  Coverage report: open htmlcov/index.html"

test-watch:
	ptw -- -x

# ── Migrations ────────────────────────────────────────────────────────────────
migrate:
	alembic upgrade head

migration:
	@read -p "Migration message: " msg; alembic revision --autogenerate -m "$$msg"

# ── Seed data ─────────────────────────────────────────────────────────────────
seed:
	python scripts/seed.py

# ── Lint ──────────────────────────────────────────────────────────────────────
lint:
	ruff check app tests
	ruff format --check app tests

fmt:
	ruff format app tests
