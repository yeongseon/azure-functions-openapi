# ------------------------
# Python and Venv Config
# ------------------------
PYTHON ?= $(shell command -v python3.12 || command -v python3.11 || command -v python3.10 || command -v python3.9 || command -v python3)

VENV_DIR = .venv

ifeq ($(OS),Windows_NT)
  VENV_BIN := $(VENV_DIR)/Scripts
else
  VENV_BIN := $(VENV_DIR)/bin
endif

UV         = $(VENV_BIN)/uv
PIP        = $(VENV_BIN)/pip
PYTHON_BIN = $(VENV_BIN)/python

# ------------------------
# Help
# ------------------------
help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ------------------------
# Setup
# ------------------------
install: ## Set up the virtual environment and install development dependencies
	@PY_VERSION=`$(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"`; \
	REQ_VERSION=3.9; \
	awk 'BEGIN { if (ARGV[1] + 0 < ARGV[2] + 0) { exit 1 } }' "$$PY_VERSION" "$$REQ_VERSION" || \
		{ echo "❌ Python >= 3.9 is required. Found $$PY_VERSION at $(PYTHON)."; exit 1; }
	@echo "✅ Using Python $$PY_VERSION at $(PYTHON)"
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install uv
	$(UV) pip install --link-mode=copy -e ".[dev]"

# ------------------------
# Quality Checks
# ------------------------
format: ## Format code using black
	$(VENV_BIN)/black src/ tests/

lint: ## Lint using ruff
	$(VENV_BIN)/ruff check src/ tests/

typecheck: ## Static type checking using mypy
	$(VENV_BIN)/mypy src/

test: ## Run tests using pytest
	PYTHONPATH=$(PWD) $(VENV_BIN)/pytest -v tests/

check: format lint typecheck coverage precommit-run ## Run all quality checks including test coverage

# ------------------------
# Cleaning
# ------------------------
clean: ## Remove caches and build artifacts
	rm -rf __pycache__/ *.egg-info .mypy_cache .pytest_cache dist build

# ------------------------
# Build
# ------------------------
dist: ## Build source and wheel distributions
	$(VENV_BIN)/hatch build

# ------------------------
# Versioning
# ------------------------
version-patch: ## Bump patch version
	$(VENV_BIN)/hatch version patch

version-minor: ## Bump minor version
	$(VENV_BIN)/hatch version minor

version-major: ## Bump major version
	$(VENV_BIN)/hatch version major

# ------------------------
# Release automation
# ------------------------
release-patch: version-patch git-release ## Patch version bump and release (commit + tag + push)
release-minor: version-minor git-release ## Minor version bump and release
release-major: version-major git-release ## Major version bump and release

git-release: ## Commit, tag, and push the release
	git add .
	git commit -m "chore: release v$(shell grep -oP '__version__ = \"\K[^\"]+' src/azure_functions_openapi/__init__.py)"
	git tag v$(shell grep -oP '__version__ = \"\K[^\"]+' src/azure_functions_openapi/__init__.py)
	git push origin main --tags

# ------------------------
# Pre-commit
# ------------------------
precommit-install: ## Install pre-commit hooks
	$(VENV_BIN)/pre-commit install

precommit-run: ## Run all pre-commit hooks on all files
	$(VENV_BIN)/pre-commit run --all-files

# ------------------------
# Changelog
# ------------------------
changelog: ## Generate CHANGELOG.md from git tags
	$(VENV_BIN)/git-changelog --output CHANGELOG.md --template keepachangelog

# ------------------------
# Test coverage
# ------------------------
coverage: ## Run tests with coverage report (text and XML + JUnit)
	PYTHONPATH=$(PWD) $(VENV_BIN)/pytest \
		--cov=src/azure_functions_openapi \
		--cov-report=term-missing \
		--cov-report=xml \
		--junitxml=junit.xml -o junit_family=legacy

coverage-html: ## Run tests with coverage and generate HTML report
	PYTHONPATH=$(PWD) $(VENV_BIN)/pytest --cov=src/azure_functions_openapi --cov-report=html

# ------------------------
# Meta
# ------------------------
show-python: ## Show which Python interpreter will be used
	@echo "Python executable: $(PYTHON)"

.PHONY: help install format lint typecheck test check clean dist \
        version-patch version-minor version-major \
        release-patch release-minor release-major git-release \
        precommit-install precommit-run changelog coverage coverage-html \
        show-python
