# Development Guide

This document provides guidance for setting up the development environment for the `azure-functions-openapi` project.

## Python Version

- This project currently uses Python 3.8.
- If you upgrade to Python 3.9+, you may need to update pre-commit hook versions accordingly.

## Local Setup

Clone and install the project in editable mode:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .
```

Then install development dependencies and pre-commit hooks:

```bash
make setup
pre-commit install
```

## Pre-commit Hooks

This project uses pre-commit to enforce code quality standards before each commit.

### Python 3.8 Compatibility

The following versions are pinned in `.pre-commit-config.yaml`:

| Tool    | Version  | Reason                             |
|---------|----------|------------------------------------|
| black   | 23.11.0  | >=24.x requires Python 3.9+        |
| bandit  | 1.7.7    | >=1.8.x requires Python 3.9+        |

If using Python 3.9+, you may run:

```bash
pre-commit autoupdate
```

Warning: Revert to compatible versions above if using Python 3.8.

### Common Commands

```bash
pre-commit run --all-files   # Run hooks on all files
pre-commit clean             # Reset hook environments
```

## Development Commands

Use the following Make targets:

```bash
make setup       # Install dev dependencies
make format      # Run black
make lint        # Run ruff
make typecheck   # Run mypy
make test        # Run pytest
```

## Project Structure

```
azure-functions-openapi/
├── src/
├── tests/
├── examples/
├── docs/
│   └── development.md
├── .pre-commit-config.yaml
└── pyproject.toml
```

## Tips

- If you encounter errors related to Python version compatibility, check `.pre-commit-config.yaml`
- Ensure your virtual environment matches the Python version constraints
