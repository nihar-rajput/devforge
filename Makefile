.PHONY: help install dev test lint type-check format clean run

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	cd backend && pip install -e .

dev: ## Install development dependencies
	cd backend && pip install -e ".[dev,gpu]"

test: ## Run all tests
	cd backend && pytest tests/ -v --cov=src --cov-report=html

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd backend && pytest tests/integration/ -v -m integration

lint: ## Run linter
	cd backend && ruff check src/ tests/

lint-fix: ## Run linter with auto-fix
	cd backend && ruff check src/ tests/ --fix

type-check: ## Run type checker
	cd backend && mypy src/ --strict

format: ## Format code
	cd backend && ruff format src/ tests/

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage

run: ## Start the backend server
	cd backend && uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

run-prod: ## Start backend in production mode
	cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1

check: lint type-check test ## Run all checks (lint + type-check + test)
