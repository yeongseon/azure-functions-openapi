# ------------------------
# Path variables
# ------------------------
PYTHON = python3.10
VENV_DIR = .venv

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
	$(VENV_DIR)/bin/pip install uv
	$(VENV_DIR)/bin/uv pip install -e ".[dev]"

# ------------------------
# Quality Checks
# ------------------------
format: ## Format code using black
	$(VENV_DIR)/bin/black src/ tests/

lint: ## Lint using ruff
	$(VENV_DIR)/bin/ruff src/ tests/

typecheck: ## Static type checking using mypy
	$(VENV_DIR)/bin/mypy src/

test: ## Run tests using pytest
	$(VENV_DIR)/bin/pytest tests/

check: format lint typecheck test ## Run all quality checks

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
	git-changelog generate --tag-pattern "v*" --output CHANGELOG.md --template keepachangelog
