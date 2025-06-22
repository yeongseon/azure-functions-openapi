# ------------------------------
# 🧰 Environment Bootstrap
# ------------------------------

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
HATCH := $(VENV_DIR)/bin/hatch

.PHONY: bootstrap
bootstrap:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "🐍 Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	fi
	@echo "📦 Ensuring Hatch is installed in virtual environment..."
	@$(PIP) install --upgrade pip > /dev/null
	@$(PIP) install hatch > /dev/null
	@echo "✅ Hatch installed at $(HATCH)"

.PHONY: ensure-hatch
ensure-hatch: bootstrap

# ------------------------------
# 🧰 Hatch Environment Management
# ------------------------------

.PHONY: install
install: ensure-hatch
	@$(HATCH) env create
	@make precommit-install

.PHONY: shell
shell: ensure-hatch
	@$(HATCH) shell

.PHONY: reset
reset: clean-all install
	@echo "🔁 Project reset complete."

.PHONY: hatch-clean
hatch-clean: ensure-hatch
	@$(HATCH) env remove || echo "⚠️ No hatch environment to remove"

# ------------------------------
# 🧪 Testing & Code Quality
# ------------------------------

.PHONY: test
test: ensure-hatch
	@$(HATCH) run test

.PHONY: cov
cov: ensure-hatch
	@$(HATCH) run cov
	@echo "📂 Open htmlcov/index.html in your browser"

.PHONY: lint
lint: ensure-hatch
	@$(HATCH) run lint

.PHONY: typecheck
typecheck: ensure-hatch
	@$(HATCH) run typecheck

.PHONY: format
format: ensure-hatch
	@$(HATCH) run format

.PHONY: check
check: lint typecheck
	@echo "✅ Lint & type check passed!"

.PHONY: check-all
check-all: check test
	@echo "✅ All checks passed including tests!"

.PHONY: precommit
precommit: ensure-hatch
	@$(HATCH) run precommit

.PHONY: precommit-install
precommit-install: ensure-hatch
	@$(HATCH) run precommit-install

# ------------------------------
# 📦 Build & Versioning
# ------------------------------

.PHONY: build
build: ensure-hatch
	@$(HATCH) build

.PHONY: version
version: ensure-hatch
	@echo "📦 Current version:"
	@$(HATCH) version

# ------------------------------
# 📝 Changelog & Tagging
# ------------------------------

.PHONY: changelog
changelog:
	@git-cliff -o CHANGELOG.md
	@echo "📝 Changelog generated."

.PHONY: commit-changelog
commit-changelog:
	@git add CHANGELOG.md
	@git commit -m "docs: update changelog" || echo "⚠️ No changes to commit"

.PHONY: tag-release
tag-release:
ifndef VERSION
	$(error VERSION is not set. Usage: make tag-release VERSION=1.0.1)
endif
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)
	@echo "🚀 Tagged release v$(VERSION)"

# ------------------------------
# 🚀 Release Automation
# ------------------------------

.PHONY: release
release: ensure-hatch
ifndef VERSION
	$(error VERSION is not set. Usage: make release VERSION=1.0.1)
endif
	@$(HATCH) version $(VERSION)
	@$(MAKE) release-core VERSION=$(VERSION)

.PHONY: release-core
release-core:
ifndef VERSION
	$(error VERSION is not set. Usage: make release-core VERSION=1.0.1)
endif
	@$(MAKE) changelog
	@$(MAKE) commit-changelog
	@$(MAKE) tag-release VERSION=$(VERSION)

.PHONY: release-patch
release-patch: ensure-hatch
	@$(HATCH) version patch
	@VERSION=$$($(HATCH) version | tail -n1); \
	git add src/**/__init__.py; \
	git commit -m "build: bump version to $$VERSION"; \
	$(MAKE) release-core VERSION=$$VERSION

.PHONY: release-minor
release-minor: ensure-hatch
	@$(HATCH) version minor
	@VERSION=$$($(HATCH) version | tail -n1); \
	git add src/**/__init__.py; \
	git commit -m "build: bump version to $$VERSION"; \
	$(MAKE) release-core VERSION=$$VERSION

.PHONY: release-major
release-major: ensure-hatch
	@$(HATCH) version major
	@VERSION=$$($(HATCH) version | tail -n1); \
	git add src/**/__init__.py; \
	git commit -m "build: bump version to $$VERSION"; \
	$(MAKE) release-core VERSION=$$VERSION

# ------------------------------
# 🚚 Publish to PyPI
# ------------------------------

.PHONY: publish-test
publish-test: ensure-hatch
	@$(HATCH) publish --repo test

.PHONY: publish-pypi
publish-pypi: ensure-hatch
	@$(HATCH) publish

# ------------------------------
# 🩺 Diagnostic & Cleanup
# ------------------------------

.PHONY: doctor
doctor:
	@echo "🔍 Python version:" && $(PYTHON) --version
	@echo "🔍 Installed packages:" && $(HATCH) env run pip list || echo "⚠️ No hatch env"
	@echo "🔍 Azure Function Core Tools version:" && func --version || echo "⚠️ func not found"
	@echo "🔍 Pre-commit hook:"
	@if [ -f .git/hooks/pre-commit ]; then echo ✅ Yes; else echo ❌ No; fi

.PHONY: clean
clean:
	@rm -rf *.egg-info dist build __pycache__ .pytest_cache

.PHONY: clean-all
clean-all: clean
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml .DS_Store $(VENV_DIR)

# ------------------------------
# 🆘 Help
# ------------------------------

.PHONY: help
help:
	@echo "📖 Available commands:" && \
	grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
