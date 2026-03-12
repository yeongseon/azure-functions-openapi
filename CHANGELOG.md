# Changelog

All notable changes to this project will be documented in this file.

## [unreleased]

## [0.13.0] - 2026-03-12

### 🚀 Features

- Add `security_scheme` parameter to `@openapi` decorator for declaring `components.securitySchemes` (#81)
- Add `security_schemes` parameter to `generate_openapi_spec()`, `get_openapi_json()`, and `get_openapi_yaml()` for central scheme definitions
- Per-decorator and central security schemes are merged automatically

### 📚 Documentation

- Document security scheme usage patterns in `docs/usage.md`
## [0.12.0] - 2026-03-08

> Note: Version `0.11.0` was published to PyPI on February 10, 2026, but its Git tag and GitHub release metadata were not preserved. Repository releases resume from `0.12.0`.

### 🚀 Features

- Allow custom OpenAPI info description

### 🐛 Bug Fixes

- Support `FunctionBuilder` inputs in the decorator
- Normalize generated route paths
- Ensure generated paths always include a leading slash
- Limit the default `200` response fallback to operations with no explicit responses
- Allow `codex/` branch names in maintenance workflows

### 📚 Documentation

- Position the project for the Azure Functions Python v2 programming model
- Add repository planning documents and align root documentation
- Add representative and complex example coverage guidance
- Replace the README demo with generated spec and Swagger UI previews
- Generate README preview assets from the representative `hello` example
- Improve development and release guidance

### 🧪 Testing

- Add smoke coverage for the representative example and the todo CRUD example
- Raise coverage for CLI and utility paths

### ⚙️ Miscellaneous Tasks

- Align tooling, maintenance workflows, and docs dependencies
- Apply remaining dependency updates
- Support manual release dispatches
- Harden release automation for explicit version releases

## [0.10.0] - 2026-02-09

### 🚀 Features

- Resolve deployment and OpenAPI security issue backlog

### 🐛 Bug Fixes

- *(ci)* Resolve lint and deploy workflow validation errors
- *(test)* Satisfy mypy type for security validation case
- *(openapi)* Preserve explicit `200` response when `response_model` exists
- *(validation)* Align fallback logs with strict behavior
- *(validation)* Disallow whitespace in route paths
- *(security)* Harden Swagger UI CSP and gate client logging
- *(metrics)* Use `PerformanceMonitor` response-time average
- *(openapi)* Drop error utilities
- *(decorator)* Preserve validation errors

### 💼 Other

- Bump version to `0.10.0`

### 🚜 Refactor

- Simplify branch strategy to GitHub Flow
- Harden registry and runtime state handling

### 📚 Documentation

- Add governance, design principles, and LSP configuration
- Fix CI badge workflow and tool versions
- Improve core documentation (index, usage, API, installation, README)
- Remove links to missing pages
- Add comprehensive examples, tutorials, and configuration guide (#67)
- Clarify supported Python versions in README
- Align quality metrics and Python support policy
- Normalize documentation casing and links
- Remove internal operations guides
- Drop non-HTTP examples
- Remove redundant examples and guides
- Drop the tutorials page
- Merge Swagger UI config into usage
- Trim API reference notes
- Link to canonical root docs
- Refresh contributing guidance
- Align changelog with cleanup
- Fix MkDocs navigation and links
- Update changelog

### ⚙️ Miscellaneous Tasks

- Add security policies and incident response (#68)
- Add performance monitoring and regression testing (#69)
- Add release process and versioning documentation (#71)
- Configure Dependabot for automated dependency updates (#72)
- Add maintenance workflows and automation (#70)
- Skip Codecov on Dependabot (#80)
- *(ci)* Route Bandit scans through the Makefile security target
- Ignore local oh-my-opencode config
- *(ci)* Pin GitHub Actions to immutable SHAs
- Remove redundant scripts directory
- Remove monitoring utilities and update docs
- Remove monitoring modules and CLI commands
- *(cli)* Remove the `validate` command and document the external validator
- Remove caching layer and update docs
- *(docs)* Remove the performance guide and related artifacts
- *(docs)* Remove monitoring references
- *(lint)* Drop unused imports

## [0.8.0] - 2026-01-22

### 🚀 Features

- Add optional OpenAPI 3.1 output support (#30)

### 📚 Documentation

- Improve the security policy with GitHub Security Advisory guidance

### 🧪 Testing

- Fix test naming and add missing module tests (#28)

### ⚙️ Miscellaneous Tasks

- Bump version to `0.8.0` and update `CHANGELOG`

## [0.7.0] - 2026-01-22

### 🚀 Features

- Add Python 3.13 and 3.14 support (#29)

### 🐛 Bug Fixes

- Correct coverage measurement configuration (#19)

### 📚 Documentation

- Add community files to the repository root (#24)

### ⚙️ Miscellaneous Tasks

- Add GitHub issue templates
- Align pre-commit hooks with `pyproject.toml` settings (#20)
- Add `py.typed` marker for PEP 561 compliance (#21)
- Add a pull request template (#23)
- Add security scanning with Dependabot and CodeQL (#25)
- Remove the obsolete `fix_tags.sh` script (#22)
- Bump version to `0.7.0` and update `CHANGELOG`

## [0.6.1] - 2026-01-22

### 💼 Other

- Bump version to `0.6.1`

### 🚜 Refactor

- Adopt Python 3.10 type hint syntax (PEP 604/585) (#9)

### 📚 Documentation

- Update changelog

## [0.6.0] - 2026-01-21

### 💼 Other

- Bump version to `0.6.0`

### 📚 Documentation

- Update changelog

### 🎨 Styling

- Format code with Ruff and Black
- Resolve lint issues
