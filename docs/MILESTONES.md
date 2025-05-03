# azure-functions-openapi – Development Checklist

## ✅ M1. Project Setup
- [x] Project scaffold with `src/`, `tests/`, and `examples/` directories
- [x] Configure `pyproject.toml`, `Makefile`, `.editorconfig`, `.gitignore`
- [x] Set Python version to >=3.8
- [x] Use `hatch` for versioning
- [x] Setup `uv` for editable install

---

## ✅ M2. Core MVP Features
- [x] `@openapi` decorator: capture `summary`, `description`, `response`
- [x] Central registry for function metadata
- [x] `/openapi.json` route for OpenAPI spec generation
- [x] `/docs` route to serve Swagger UI
- [x] Create example Azure Function

---

## ⬜ M3. Extended Features
- [ ] Path and method inference from Azure triggers
- [ ] Type hint / `pydantic` based schema generation
- [ ] Support for query/path/requestBody parameters
- [ ] Register error responses (e.g., 400, 500)
- [ ] Add OpenAPI 3.1 support (optional)

---

## ⬜ M4. Quality & CI
- [ ] Add `pytest` unit tests
- [ ] Integrate GitHub Actions CI
- [ ] Measure coverage and add badge
- [ ] Set up `pre-commit` hooks for lint, format, type-check

---

## ⬜ M5. Release & Documentation
- [ ] Add usage examples to `README.md`
- [ ] Add Swagger UI screenshot / preview
- [ ] Build package using `hatch build`
- [ ] Publish to PyPI
- [ ] (Optional) Host Swagger UI demo (e.g., GitHub Pages)

---

## ⏱️ Version Plan
- [ ] **v0.1.0** – Core MVP
- [ ] **v0.2.0** – Inference + Type schema
- [ ] **v0.3.0** – Error handling, customization
- [ ] **v1.0.0** – Production-ready with full test coverage
