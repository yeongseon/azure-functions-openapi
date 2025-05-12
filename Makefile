# ------------------------
# Path variables
# ------------------------
PYTHON     ?= python3.9
VENV_DIR   = .venv
UV         = $(VENV_DIR)/bin/uv
PIP        = $(VENV_DIR)/bin/pip
PYTHON_BIN = $(VENV_DIR)/bin/python

# ------------------------
# Help
# ------------------------
help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ------------------------
# Setup
# ------------------------
install: ## Set up the virtual environment and install development dependencies
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install uv
	$(UV) pip install --link-mode=copy -e ".[dev]"

# ------------------------
# Quality Checks
# ------------------------
format: ## Format code using black
	$(VENV_DIR)/bin/black src/ tests/

lint: ## Lint using ruff
	$(VENV_DIR)/bin/ruff check src/ tests/

typecheck: ## Static type checking using mypy
	$(VENV_DIR)/bin/mypy src/

test: ## Run tests using pytest
	PYTHONPATH=$(PWD) $(VENV_DIR)/bin/pytest -v tests/

check: format lint typecheck coverage ## Run all quality checks including test coverage

# ------------------------
# Cleaning
# ------------------------
clean: ## Remove caches and build artifacts
	rm -rf __pycache__/ *.egg-info .mypy_cache .pytest_cache dist build

# ------------------------
# Build
# ------------------------
dist: ## Build source and wheel distributions
	$(VENV_DIR)/bin/hatch build

# ------------------------
# Versioning
# ------------------------
version-patch: ## Bump patch version
	$(VENV_DIR)/bin/hatch version patch

version-minor: ## Bump minor version
	$(VENV_DIR)/bin/hatch version minor

version-major: ## Bump major version
	$(VENV_DIR)/bin/hatch version major

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
	$(VENV_DIR)/bin/pre-commit install

precommit-run: ## Run all pre-commit hooks on all files
	$(VENV_DIR)/bin/pre-commit run --all-files

# ------------------------
# Changelog
# ------------------------
changelog: ## Generate CHANGELOG.md from git tags
	$(VENV_DIR)/bin/git-changelog --output CHANGELOG.md --template keepachangelog

# ------------------------
# Test coverage
# ------------------------
coverage: ## Run tests with coverage report (text and XML + JUnit)
	PYTHONPATH=$(PWD) $(VENV_DIR)/bin/pytest \
		--cov=src/azure_functions_openapi \
		--cov-report=term-missing \
		--cov-report=xml \
		--junitxml=junit.xml -o junit_family=legacy

coverage-html: ## Run tests with coverage and generate HTML report
	PYTHONPATH=$(PWD) $(VENV_DIR)/bin/pytest --cov=src/azure_functions_openapi --cov-report=html
