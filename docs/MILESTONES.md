# azure-functions-openapi – Development Checklist

## ✅ M1. Project Setup
- [x] Project scaffold with `src/`, `tests/`, and `examples/` directories
- [x] Configure `pyproject.toml`, `Makefile`, `.editorconfig`, `.gitignore`
- [x] Set Python version to >=3.8
- [x] Use `hatch` for versioning
- [x] Setup `uv` for editable install
- [x] Add `.pre-commit-config.yaml` and basic hooks

---

## ✅ M2. Core MVP Features (v0.2.0)
- [x] `@openapi` decorator: capture `summary`, `description`, `response`
- [x] Central registry for function metadata
- [x] `/openapi.json` route for OpenAPI spec generation
- [x] `/docs` (`/swagger`) route to serve Swagger UI
- [x] Create example Azure Function

---

## ⬜ M3. Extended Features (v0.3.0)
- [x] Inference of HTTP method and route path from Azure trigger
- [x] Support for `parameters` (query/path/header)
- [x] Support for `requestBody` specification
- [x] Define response schemas (e.g. JSON schema, examples)
- [x] Integrate with `pydantic` or type hints
- [x] Custom tags, operationId
- [x] Markdown `description` support
- [x] Parameter type expansion: `cookie` (remaining type)
- [x] YAML output (`/openapi.yaml` endpoint)

---

## ⬜ M4. Quality & CI (v0.4.0)
- [x] Makefile targets: `format`, `lint`, `typecheck`, `test`, `check`
- [x] `pre-commit` hooks (`black`, `ruff`, `mypy`, etc.)
- [x] Add `pytest` unit tests for decorators and generator
- [ ] Integrate GitHub Actions CI workflow
- [ ] Measure test coverage and add badge

---

## ⬜ M5. Release & Documentation
- [x] `hatch build` for packaging
- [x] Add `README.md` usage examples and basic documentation
- [x]  Add docs/ folder with index.md, usage.md, contributing.md
- [x]  Add mkdocs.yml for structured site docs
- [ ] Add Swagger UI screenshot/preview
- [ ] Add CHANGELOG generator with `git-changelog`
- [ ] Publish first release to PyPI
- [ ] Improve Swagger UI rendering (examples, schema preview, rich formatting)
- [ ] (Optional) Host demo of Swagger UI (e.g., GitHub Pages or Azure Static Web App)

---

## ⬜ M6. OpenAPI 3.1 & Compatibility (v0.4.0+)
- [ ] OpenAPI 3.1 support (e.g., `$schema`, JSON Schema 2020-12)
- [ ] OpenAPI version selection (3.0 / 3.1 toggle)
