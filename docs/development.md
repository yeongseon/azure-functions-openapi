# Development Guide

This document provides guidance for setting up the development environment for the `azure-functions-openapi` project.

## Python Version

- This project supports Python 3.9+.
- All development and formatting tools are configured accordingly via [Hatch](https://hatch.pypa.io/).

## Local Setup

Clone and set up the project:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi

# Install Hatch (if not installed)
pip install hatch

# Create environment and install dev dependencies
make install
```

Install pre-commit hooks:

```bash
make precommit-install
```

## Pre-commit Hooks Overview

This project uses pre-commit to ensure consistent code quality across formatting, linting, typing, and security.

| Tool   | Version   | Purpose                          |
|--------|-----------|----------------------------------|
| black  | 23.11.0   | Auto-code formatter              |
| ruff   | v0.4.4    | Linter + import sorter + fixer  |
| mypy   | v1.15.0   | Static type checker              |
| bandit | 1.7.7     | Security checker on `src/` only  |

### Bandit Configuration

- Only scans `src/` directory
- Skips `tests/`
- Uses `pass_filenames: false` for full-directory analysis

### Run Hooks Manually

```bash
make precommit
pre-commit clean
```

## Development Commands

Makefile provides shortcuts for common development tasks:

```bash
make install           # Set up Hatch environment and dev dependencies
make format            # Format code (ruff + black)
make lint              # Run linter (ruff + mypy)
make typecheck         # Run mypy type checking
make test              # Run pytest
make cov               # Run tests with coverage
make check             # Run lint + typecheck
make check-all         # Run lint + typecheck + test + coverage
make docs              # Start MkDocs dev server
make build             # Build package
make release-patch     # Version bump + tag + push (patch)
make precommit         # Run all pre-commit hooks
make precommit-install # Install pre-commit hooks
```

## Project Structure

```
azure-functions-openapi/
├── src/
├── tests/
├── examples/
├── docs/
│   └── development.md
├── .github/
│   └── workflows/
├── .pre-commit-config.yaml
├── Makefile
├── pyproject.toml
└── README.md
```

## Tips

- Ensure you're using Python 3.9+.
- Use `make check-all` before committing to validate your changes.
- Prefer `make` commands to ensure consistent dev experience across platforms.
