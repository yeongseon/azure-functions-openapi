# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

### 💼 Other

- Bump version to 0.6.0

### 🎨 Styling

- Format code with ruff and black
- Resolve lint issues

### ⚙️ Miscellaneous Tasks

- Fix mypy strict type checks
- Drop python 3.9 support

## [0.5.1] - 2026-01-21

### 🐛 Bug Fixes

- Normalize pydantic schemas into components

### 💼 Other

- Bump version to 0.5.1

### 📚 Documentation

- Enhance documentation with comprehensive guides
- Update changelog

## [0.5.0] - 2025-09-04

### 🚀 Features

- Add comprehensive error handling system
- Add high-performance caching system
- Enhance Swagger UI security and input validation
- Add server info, monitoring, and CLI tools
- Enhance OpenAPI generation with caching and error handling

### 💼 Other

- Bump version to 0.5.0

### 📚 Documentation

- Update changelog
- Add comprehensive documentation and update configuration
- Update changelog

### ⚙️ Miscellaneous Tasks

- Fix version check path in release workflow
- *(docs)* Fix hatch run by removing nonexistent docs env

## [0.4.1] - 2025-06-22

### 🐛 Bug Fixes

- *(makefile)* Correct Python version check to support 3.9+

### 💼 Other

- *(makefile)* Add Hatch-based automation for test, build, release
- *(pyproject)* Configure hatch build and publish targets
- Bump version to 0.4.1

### 📚 Documentation

- Update development guide to reflect Hatch and Makefile integration

### ⚙️ Miscellaneous Tasks

- Improve Makefile with Python 3.9+ check, .PHONY, and cross-platform venv support
- *(build)* Clean up config and align with Hatch-based Makefile execution
- *(ci)* Replace test.yml with ci-test.yml for clarity and maintainability
- *(docs)* Rename deploy-docs.yml to docs.yml for clearer workflow separation
- *(docs)* Reuse Makefile install step in docs workflow
- Add GitHub Actions release workflow

## [0.4.0] - 2025-05-13

### 🚀 Features

- *(example)* Add todo_api with create and list endpoints
- *(example)* Add complete CRUD implementation to todo_crud_api example
- Add Pydantic v1/v2 compatibility and schema utils
- Add Swagger UI support and update example functions

### 🐛 Bug Fixes

- Add type hints and support Pydantic v2, clean test/lint output
- *(openapi)* Avoid requestBody for GET methods
- *(example)* Resolve double /api prefix and update route in spec
- Move isort settings under lint section in pyproject.toml

### 💼 Other

- Add coverage and coverage-html targets to Makefile

### 🚜 Refactor

- *(example)* Apply typed openapi decorator to fix mypy issue
- *(example)* Drop Pydantic dependency and polish Markdown description
- *(examples)* Replace obsolete openapi_json sample with hello_openapi and update tests
- *(decorator)* Reorder parameters and registry keys for clarity
- *(openapi)* Remove hard-coded /api base path and servers entry
- *(example)* Rename todo_api to todo_crud_api

### 📚 Documentation

- Split development instructions into development.md
- Enhance index.md with project overview and documentation links
- Add detailed docstrings and usage examples to decorator and openapi modules
- Add mkdocs.md with instructions for local preview and GitHub Pages deployment
- Add badges to README for PyPI, CI, Docs, and License
- *(todo_api)* Add detailed docstrings for all endpoints and models
- Add Quick Start section and refresh README badges
- Add file header comment to decorator.py
- Add comprehensive Usage Guide (docs/usage_guide.md)
- *(decorator)* Expand example section with Hello World and Pydantic CRUD
- *(readme)* Clarify that only Pydantic v2 is supported
- Restructure mkdocs.yml with full nav and example sections
- Add placeholder markdown files to fix mkdocs build warnings
- Restructure documentation with updated README and index
- Update development checklist in English and reflect current progress
- *(readme)* Revise Quick Start example
- *(readme)* Fix unclosed code block after function example
- *(readme)* Remove collapsed quickstart section and refine examples
- Update full documentation and add OpenAPI preview

### 🎨 Styling

- *(readme)* Remove duplicate horizontal rules before Quick Start

### 🧪 Testing

- Add pytest-cov and configure coverage report for Codecov
- Align OpenAPI tests with /api prefix and enable pytest -v

### ⚙️ Miscellaneous Tasks

- Update pre-commit hook versions
- Add test workflow directory and GitHub Actions test.yml
- Fix import error by adding PYTHONPATH for examples
- Debug coverage.xml generation and allow 0% threshold
- Verify mkdocs build before deploy and add [docs] extra to pyproject.toml
- Switch to make coverage in GitHub Actions workflow
- Update dependencies or project settings
- *(pre-commit)* Configure mypy to use pyproject.toml
- *(mypy)* Exclude examples directory from type checking
- Run tests in dedicated venv to fix Makefile coverage path
- Add Codecov upload step with v5 action
- Fix Codecov upload path and add .coveragerc
- *(codecov)* Add codecov.yml with build_root and status thresholds
- *(docs)* Pin MkDocs build workflow to Python 3.8
- *(coverage)* Ensure relative paths in coverage.xml via .coveragerc
- *(codecov)* Switch to tokenless upload so fork PRs report coverage
- *(codecov)* Simplify upload step and rely on auto file detection
- *(codecov)* Upload JUnit test results to Codecov for test insights
- Add multi-version test support for Python 3.9–3.12
- Upload coverage to Codecov only from Python 3.9 job
- Update ruff settings for Python 3.9, improve import sorting, and adjust linting options
- Update imports and apply quality checks using ruff, black, mypy, and pytest
- Add pre-commit run to check command in Makefile
- Update pre-commit config to include black, ruff, mypy, and bandit
- Add junit.xml to .gitignore
- Release v0.4.0
- Release v0.4.0

## [0.3.0] - 2025-05-07

### 🚀 Features

- Support OpenAPI parameters and requestBody in decorator and schema
- Support response schema and examples in OpenAPI output
- Infer HTTP method and route path from decorator metadata
- Implement automatic inference of route and method from function app metadata
- Support operationId and tags in OpenAPI spec with tests
- Support markdown in description and update related OpenAPI spec tests
- Add /openapi.yaml endpoint to return OpenAPI spec in YAML format

### 📚 Documentation

- Generate changelog for v0.2.0
- Update MILESTONES.md to reflect v0.2.0 completion and outline M3 goals
- Update milestones.md with latest project roadmap
- Update milestones.md with latest project roadmap
- Add full documentation with index, usage, contributing and mkdocs config

### 🧪 Testing

- Add tests/ directory for unit tests
- Add test for OpenAPI schema generation using Pydantic models
- Add OpenAPI spec test for cookie parameter support

### ⚙️ Miscellaneous Tasks

- Fix changelog generation to use local git-changelog binary
- Fix PYTHONPATH for tests and add __init__.py files
- Ignore .github and .vscode directories
- Add mypy config to ignore missing imports for PyYAML
- Release v0.3.0

## [0.2.0] - 2025-05-03

### 🚀 Features

- Add OpenAPI decorator and spec generator with example function

### 📚 Documentation

- Add development milestones checklist
- Update milestones for v0.2.0

### ⚙️ Miscellaneous Tasks

- Add hatch-based versioning support
- Set initial version in __init__.py
- Update Makefile with uv install and versioning commands
- *(build)* Remove static version to enable hatch versioning
- *(release)* Bump version to 0.1.1
- *(makefile)* Add versioning, changelog, and release automation commands
- *(pyproject)* Add git-changelog to dev dependencies
- Add pre-commit configuration
- Update ruff lint command to use 'check' subcommand
- Normalize line endings to LF using .editorconfig
- Release v0.2.0

<!-- generated by git-cliff -->
