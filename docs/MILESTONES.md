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
- [ ] Inference of HTTP method and route path from Azure trigger
- [ ] Support for `parameters` (query/path/header)
- [ ] Support for `requestBody` specification
- [ ] Define response schemas (e.g. JSON schema, examples)
- [ ] Optional: Integrate with `pydantic` or type hints
- [ ] Optional: OpenAPI 3.1 support
- [ ] Optional: Custom tags, operationId

---

## ⬜ M4. Quality & CI
- [x] Makefile targets: `format`, `lint`, `typecheck`, `test`, `check`
- [x] `pre-commit` hooks (`black`, `ruff`, `mypy`, etc.)
- [ ] Add `pytest` unit tests for decorators and generator
- [ ] Integrate GitHub Actions CI workflow
- [ ] Measure test coverage and add badge

---

## ⬜ M5. Release & Documentation
- [x] `hatch build` for packaging
- [ ] Add `README.md` usage examples and basic documentation
- [ ] Add Swagger UI screenshot/preview
- [ ] Add CHANGELOG generator with `git-changelog`
- [ ] Publish first release to PyPI
- [ ] (Optional) Host demo of Swagger UI (e.g., GitHub Pages or Azure Static Web App)

---

## ⏱️ Version Plan
- [x] **v0.1.0** – Initial setup
- [x] **v0.2.0** – Core MVP (decorator, registry, JSON + Swagger UI)
- [ ] **v0.3.0** – Extended OpenAPI features (inference, parameters, schema)
- [ ] **v1.0.0** – Production-ready with full test coverage, PyPI release
