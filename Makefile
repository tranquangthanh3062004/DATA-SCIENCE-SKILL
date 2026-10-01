# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ADI-OS — Development Command Center                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

.PHONY: help install lint format test test-unit test-integration test-quality \
        docker-up docker-down dbt-run dbt-test quality-check serve clean

PYTHON := python
UV := uv

# ── Default ──────────────────────────────────────────────────────────────
help: ## Show this help message
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║  ADI-OS Development Commands                            ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────────────────────────────
install: ## Install all dependencies (dev mode)
	$(UV) sync --all-extras
	$(UV) run pre-commit install

install-prod: ## Install production dependencies only
	$(UV) sync

# ── Code Quality ─────────────────────────────────────────────────────────
lint: ## Run linter (ruff)
	$(UV) run ruff check src/ tests/

format: ## Auto-format code (ruff)
	$(UV) run ruff format src/ tests/
	$(UV) run ruff check --fix src/ tests/

typecheck: ## Run type checking (mypy)
	$(UV) run mypy src/

# ── Testing ──────────────────────────────────────────────────────────────
test: ## Run all tests
	$(UV) run pytest

test-unit: ## Run unit tests only
	$(UV) run pytest -m unit

test-integration: ## Run integration tests only
	$(UV) run pytest -m integration

test-quality: ## Run data quality gate tests
	$(UV) run pytest -m data_quality

test-ml: ## Run ML pipeline tests
	$(UV) run pytest -m ml

# ── Data Quality ─────────────────────────────────────────────────────────
quality-check: ## Run data quality checks (Great Expectations + Soda)
	$(UV) run $(PYTHON) -m src.quality.run_checks

profile-data: ## Profile dataset and generate DATA_QUALITY_REPORT.md
	$(UV) run $(PYTHON) -m src.quality.profiler

# ── dbt ──────────────────────────────────────────────────────────────────
dbt-run: ## Run dbt models (Bronze → Silver → Gold)
	cd dbt_project && dbt run

dbt-test: ## Run dbt tests
	cd dbt_project && dbt test

dbt-docs: ## Generate and serve dbt documentation
	cd dbt_project && dbt docs generate && dbt docs serve

# ── ML Pipeline ──────────────────────────────────────────────────────────
train: ## Run ML training pipeline
	$(UV) run $(PYTHON) -m src.ml.training.run_experiment

evaluate: ## Run model evaluation
	$(UV) run $(PYTHON) -m src.ml.evaluation.run_evaluation

# ── Serving ──────────────────────────────────────────────────────────────
serve: ## Start model serving API
	$(UV) run uvicorn src.serving.app:app --host 0.0.0.0 --port 8000 --reload

# ── Docker ───────────────────────────────────────────────────────────────
docker-up: ## Start local development stack
	docker compose up -d

docker-down: ## Stop local development stack
	docker compose down

docker-build: ## Build all Docker images
	docker compose build

# ── Documentation ────────────────────────────────────────────────────────
docs-serve: ## Serve documentation locally
	$(UV) run mkdocs serve

docs-build: ## Build documentation site
	$(UV) run mkdocs build

# ── Cleanup ──────────────────────────────────────────────────────────────
clean: ## Remove build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ htmlcov/ reports/
	@echo "✅ Cleaned all build artifacts"
