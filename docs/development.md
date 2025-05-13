# Development Guide

This document provides guidance for setting up the development environment for the `azure-functions-openapi` project.

## Python Version

- This project supports Python 3.9+.
- All development and formatting tools are configured accordingly.

## Local Setup

Clone and install the project in editable mode:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .[dev]
```

Install pre-commit hooks:

```bash
make setup
pre-commit install
```

## Pre-commit Hooks Overview

This project uses pre-commit to ensure consistent code quality across formatting, linting, typing, and security.

| Tool   | Version   | Purpose                   |
|--------|-----------|---------------------------|
| black  | 23.11.0   | Auto-code formatter       |
| ruff   | v0.4.4    | Linter + auto-fix         |
| mypy   | v1.15.0   | Static type checker       |
| bandit | 1.7.7     | Security checker on `src/` only |

### Bandit Configuration

- Only scans `src/` directory
- Skips `tests/`
- Uses `pass_filenames: false` for full-directory analysis

### Run Hooks Manually

```bash
pre-commit run --all-files   # Run on all files
pre-commit clean             # Reset environments
```

## Development Commands

Makefile provides shortcuts for common development tasks:

```bash
make install          # Set up venv and install dev dependencies
make format           # Format code using black
make lint             # Run ruff linter
make typecheck        # Static type checking with mypy
make test             # Run pytest
make check            # Run format, lint, typecheck, test, and coverage
make coverage         # Run tests with coverage reporting
make coverage-html    # Generate HTML coverage report
make dist             # Build source and wheel distributions
make changelog        # Generate CHANGELOG.md from git tags
make precommit-run    # Run all pre-commit hooks
make release-patch    # Automate patch release (commit + tag + push)
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
├── Makefile
└── pyproject.toml
```

## Tips

- Ensure you're using Python 3.9+.
- Use `make check` to quickly validate your changes.
- Prefer `make` over manually running commands to ensure consistency.
