# Create a virtual environment and install the project in editable mode with development dependencies
install:
	python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

# Format Python code using Black
format:
	black src/ tests/

# Lint Python code using Ruff
lint:
	ruff src/ tests/

# Perform static type checking using MyPy
typecheck:
	mypy src/

# Run tests using Pytest
test:
	pytest tests/

# Run all quality checks: format, lint, type check, and tests
check: format lint typecheck test

# Bump version using hatch
version-patch:
	hatch version patch

version-minor:
	hatch version minor

version-major:
	hatch version major
