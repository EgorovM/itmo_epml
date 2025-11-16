.PHONY: help install install-dev setup pre-commit-install format lint type-check security-check test clean docker-build docker-up docker-down docker-shell run-notebook

# Variables
PYTHON := python3
UV := uv
DOCKER_COMPOSE := docker-compose

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install project dependencies using uv
	$(UV) pip install -e .

install-dev: ## Install development dependencies
	$(UV) pip install -e ".[dev]"

setup: install-dev pre-commit-install ## Complete setup: install dependencies and pre-commit hooks
	@echo "Setup complete!"

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

format: ## Format code with black and isort
	black src tests
	isort src tests

lint: ## Run ruff linter
	ruff check src tests

lint-fix: ## Run ruff linter and fix issues
	ruff check --fix src tests

type-check: ## Run mypy type checker
	mypy src

security-check: ## Run bandit security checker
	bandit -r src -f json -o bandit-report.json

check: format lint type-check security-check ## Run all checks (format, lint, type-check, security)

test: ## Run tests with pytest
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	rm -rf build dist .coverage htmlcov bandit-report.json

docker-build: ## Build Docker image
	docker build -t epml:latest .

docker-up: ## Start Docker containers
	$(DOCKER_COMPOSE) up -d

docker-down: ## Stop Docker containers
	$(DOCKER_COMPOSE) down

docker-logs: ## Show Docker logs
	$(DOCKER_COMPOSE) logs -f

docker-shell: ## Open shell in Docker container
	docker exec -it epml-jupyter /bin/bash

run-notebook: ## Run Jupyter Lab locally
	jupyter lab --ip=0.0.0.0 --port=8888

run-notebook-docker: docker-up ## Run Jupyter Lab in Docker
	@echo "Jupyter Lab is running at http://localhost:8888"

sync: ## Sync dependencies and update lock file
	$(UV) pip sync pyproject.toml

update: ## Update dependencies
	$(UV) pip install --upgrade -e ".[dev]"

requirements: ## Generate requirements.txt from pyproject.toml
	$(UV) pip compile pyproject.toml -o requirements.txt
	$(UV) pip compile pyproject.toml --extra dev -o requirements-dev.txt

all: clean install-dev pre-commit-install check test ## Run full pipeline: clean, install, check, test
