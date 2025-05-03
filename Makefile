# Path variables
PYTHON = python3.10
VENV_DIR = .venv

install:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install uv
	$(VENV_DIR)/bin/uv pip install -e ".[dev]"

format:
	$(VENV_DIR)/bin/black src/ tests/

lint:
	$(VENV_DIR)/bin/ruff src/ tests/

typecheck:
	$(VENV_DIR)/bin/mypy src/

test:
	$(VENV_DIR)/bin/pytest tests/

check: format lint typecheck test

clean:
	rm -rf __pycache__/ *.egg-info .mypy_cache .pytest_cache dist build

dist:
	$(VENV_DIR)/bin/hatch build

# Versioning
version-patch:
	$(VENV_DIR)/bin/hatch version patch

version-minor:
	$(VENV_DIR)/bin/hatch version minor

version-major:
	$(VENV_DIR)/bin/hatch version major

# Release automation
release-patch: version-patch git-release
release-minor: version-minor git-release
release-major: version-major git-release

git-release:
	git add .
	git commit -m "chore: release v$(shell grep -oP '__version__ = \"\K[^\"]+' src/azure_functions_openapi/__init__.py)"
	git tag v$(shell grep -oP '__version__ = \"\K[^\"]+' src/azure_functions_openapi/__init__.py)"
	git push origin main --tags

# Pre-commit
precommit-install:
	$(VENV_DIR)/bin/pre-commit install

precommit-run:
	$(VENV_DIR)/bin/pre-commit run --all-files
