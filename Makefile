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

dvc-init: ## Initialize DVC
	$(UV) run dvc init --no-scm

dvc-add-data: ## Add data to DVC tracking
	dvc add data/raw/iris.csv || echo "Data file may not exist, creating example..."
	@mkdir -p data/raw
	@touch data/raw/iris.csv || true

dvc-repro: ## Reproduce DVC pipeline
	dvc repro

dvc-push: ## Push data to remote storage
	dvc push

dvc-pull: ## Pull data from remote storage
	dvc pull

mlflow-ui: ## Start MLflow UI
	mlflow ui --host 0.0.0.0 --port 5000

mlflow-compare: ## Compare model versions
	python src/models/compare_models.py

train-pipeline: ## Run full training pipeline (prepare data + train)
	python src/data/prepare_data.py
	python src/models/train_with_mlflow.py

run-experiments: ## Run all ML experiments
	python src/experiments/run_experiments.py

compare-experiments: ## Compare and filter experiments
	python src/experiments/compare_experiments.py

mlflow-ui-db: ## Start MLflow UI with SQLite database
	mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000

reset-mlflow-db: ## Reset MLflow database (fix migration errors)
	python scripts/reset_mlflow_db.py

pipeline-run: ## Run complete pipeline with Hydra
	python src/pipeline/run_pipeline.py

pipeline-train: ## Train model with specific config (usage: make pipeline-train MODEL=random_forest)
	python src/pipeline/train_with_config.py model=$(MODEL)

pipeline-all: ## Run pipeline for all models
	python src/pipeline/run_all_models.py

pipeline-validate: ## Validate configuration
	python -c "from src.pipeline.validate_config import validate_config, compose_configs; cfg = compose_configs(); result = validate_config(cfg); print('Valid:', result['valid']); print('Errors:', result['errors']); print('Warnings:', result['warnings'])"

clearml-setup: ## Setup ClearML configuration
	python -c "from src.clearml_utils.setup import get_clearml_config; import json; print(json.dumps(get_clearml_config(), indent=2))"

clearml-experiments: ## Run experiments with ClearML
	python src/clearml_utils/run_experiments.py

clearml-compare: ## Compare ClearML experiments
	python src/clearml_utils/compare_experiments.py

clearml-train: ## Train single model with ClearML
	python src/clearml_utils/train_with_clearml.py

clearml-pipeline: ## Create and run ClearML pipeline
	python scripts/run_clearml_pipeline.py

clearml-pipeline-auto: ## Automatically create, run, and monitor ClearML pipeline
	python scripts/run_clearml_pipeline_auto.py --monitor --wait

clearml-pipeline-monitor: ## Monitor ClearML pipeline (usage: make clearml-pipeline-monitor PIPELINE_ID=xxx)
	python -c "from src.clearml_utils.pipeline_monitor import ClearMLPipelineMonitor; import sys; monitor = ClearMLPipelineMonitor(); result = monitor.monitor_pipeline('$(PIPELINE_ID)', check_interval=10); print(f'Status: {result}')"

clearml-agent-init: ## Initialize ClearML agent (first time setup)
	clearml-agent init

clearml-agent-start: ## Start ClearML agent for default queue
	@echo "Starting ClearML agent for queue 'default'..."
	@echo "Press Ctrl+C to stop"
	clearml-agent daemon --queue default

clearml-agent-stop: ## Stop ClearML agent
	@echo "Stopping ClearML agent..."
	@pkill -f "clearml-agent" || echo "No agent process found"

all: clean install-dev pre-commit-install check test ## Run full pipeline: clean, install, check, test
