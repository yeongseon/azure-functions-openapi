# Changelog

All notable changes to this project are documented here. This changelog follows
[Keep a Changelog](https://keepachangelog.com/) and the project adheres to
[Semantic Versioning](https://semver.org/).

## [0.13.0] - 2026-03-12

### Features

- Add `security_scheme` parameter to `@openapi` decorator for declaring `components.securitySchemes` (#81).
- Add `security_schemes` parameter to `generate_openapi_spec()`, `get_openapi_json()`, and `get_openapi_yaml()` for central scheme definitions.
- Per-decorator and central security schemes are merged automatically.

### Documentation

- Document security scheme usage patterns in `docs/usage.md`.

## [0.12.0] - 2026-03-08

### Features

- Allow custom OpenAPI info description via the `description` parameter.

### Bug Fixes

- Support `FunctionBuilder` inputs in the decorator.
- Normalize generated route paths to always include a leading slash.
- Limit the default `200` response fallback to operations with no explicit responses.
- Allow `codex/` branch names in maintenance workflows.

### Documentation

- Position the project for the Azure Functions Python v2 programming model.
- Add repository planning documents and align root documentation.
- Replace the README demo with generated spec and Swagger UI previews.
- Generate README preview assets from the representative `hello` example.
- Improve development and release guidance.

### Testing

- Add smoke coverage for the representative example and the todo CRUD example.
- Raise coverage for CLI and utility paths.

### Miscellaneous

- Align tooling, maintenance workflows, and docs dependencies.
- Support manual release dispatches.
- Harden release automation for explicit version releases.

## [0.10.0] - 2026-02-09

### Features

- Resolve deployment and OpenAPI security issue backlog.

### Bug Fixes

- Resolve lint and deploy workflow validation errors.
- Satisfy mypy type for security validation case.
- Preserve explicit `200` response when `response_model` exists.
- Align fallback logs with strict behavior.
- Disallow whitespace in route paths.
- Harden Swagger UI CSP and gate client logging.
- Use `PerformanceMonitor` response-time average.
- Drop error utilities.
- Preserve validation errors in decorator.

### Refactor

- Simplify branch strategy to GitHub Flow.
- Harden registry and runtime state handling.

### Documentation

- Add governance, design principles, and LSP configuration.
- Fix CI badge workflow and tool versions.
- Improve core documentation (index, usage, API, installation, README).
- Add comprehensive examples, tutorials, and configuration guide (#67).
- Clarify supported Python versions in README.

### Miscellaneous

- Add security policies and incident response (#68).
- Add performance monitoring and regression testing (#69).
- Add release process and versioning documentation (#71).
- Configure Dependabot for automated dependency updates (#72).
- Add maintenance workflows and automation (#70).
- Skip Codecov on Dependabot PRs (#80).
- Pin GitHub Actions to immutable SHAs.
- Remove monitoring utilities and CLI commands.
- Remove the `validate` CLI command (use external validators).
- Remove caching layer.

## [0.8.0] - 2026-01-22

### Features

- Add optional OpenAPI 3.1 output support (#30).

### Documentation

- Improve the security policy with GitHub Security Advisory guidance.

### Testing

- Fix test naming and add missing module tests (#28).

## [0.7.0] - 2026-01-22

### Features

- Add Python 3.13 and 3.14 support (#29).

### Bug Fixes

- Correct coverage measurement configuration (#19).

### Documentation

- Add community files to the repository root (#24).

### Miscellaneous

- Add GitHub issue templates.
- Align pre-commit hooks with `pyproject.toml` settings (#20).
- Add `py.typed` marker for PEP 561 compliance (#21).
- Add a pull request template (#23).
- Add security scanning with Dependabot and CodeQL (#25).
- Remove the obsolete `fix_tags.sh` script (#22).

## [0.6.1] - 2026-01-22

### Refactor

- Adopt Python 3.10 type hint syntax (PEP 604/585) (#9).

## [0.6.0] - 2026-01-21

### Styling

- Format code with Ruff and Black.
- Resolve lint issues.
