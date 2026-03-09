.PHONY: dev test format lint typecheck check migrate seed install

# Run the FastAPI dev server
dev:
	uvicorn app.main:app --reload

# Run test suite
test:
	python -m pytest tests/ -v

# Auto-format code with black
format:
	black app/ tests/ scripts/

# Lint with ruff (and auto-fix safe issues)
lint:
	ruff check app/ tests/ scripts/ --fix

# Type check with mypy
typecheck:
	mypy app/

# Run all quality checks (what CI would run)
check: format lint typecheck

# Apply database migrations
migrate:
	alembic upgrade head

# Seed the database with fake data
seed:
	python -m scripts.seed

# Install all dependencies + pre-commit hooks
install:
	pip install -e ".[dev]"
	pre-commit install
