# azure-functions-openapi – Development Checklist

## ✅ M1. Project Setup
- [x] Scaffold the project with `src/`, `tests/`, and `examples/` directories
- [x] Configure `pyproject.toml`, `Makefile`, `.editorconfig`, `.gitignore`
- [x] Set Python version to >=3.8
- [x] Use `hatch` for versioning
- [x] Set up `uv` for editable installs
- [x] Add `.pre-commit-config.yaml` and essential hooks

---

## ✅ M2. Core MVP Features (v0.2.0)
- [x] Implement `@openapi` decorator: support `summary`, `description`, `response`
- [x] Build central registry for function metadata
- [x] Provide `/openapi.json` route to serve OpenAPI spec
- [x] Serve Swagger UI at `/docs` (`/swagger`)
- [x] Create example Azure Function with decorated route

---

## ✅ M3. Extended Features (v0.3.0)
- [x] Automatically infer HTTP method and route from Azure trigger
- [x] Add support for request parameters: query, path, header
- [x] Enable `requestBody` support with schema validation
- [x] Support JSON schema for responses (including `examples`)
- [x] Integrate with `pydantic` or type annotations
- [x] Allow custom tags and `operationId`
- [x] Support Markdown in descriptions
- [x] Expand parameter location support (`cookie` params)
- [x] Provide `/openapi.yaml` endpoint for YAML format

---

## ✅ M4. Quality & CI (v0.4.0)
- [x] Add Makefile targets: `format`, `lint`, `typecheck`, `test`, `check`
- [x] Integrate `pre-commit` hooks (`black`, `ruff`, `mypy`, etc.)
- [x] Write unit tests with `pytest` for decorators and OpenAPI generator
- [x] Add GitHub Actions CI pipeline
- [x] Generate coverage report and add Codecov badge

---

## ⬜ M5. Release & Documentation
- [x] Build package with `hatch build`
- [x] Provide usage examples and instructions in `README.md`
- [x] Create `docs/` folder with `index.md`, `usage.md`, `contributing.md`
- [x] Add `mkdocs.yml` to structure documentation site
- [ ] Add Swagger UI screenshot or visual preview to docs
- [ ] Automate changelog generation with `git-changelog`
- [ ] Publish first release to PyPI
- [ ] Improve Swagger UI rendering (rich `examples`, schema previews)
- [ ] (Optional) Host demo site using GitHub Pages or Azure Static Web App

---

## ⬜ M6. OpenAPI 3.1 & Compatibility (v0.4.0+)
- [ ] Support OpenAPI 3.1 (`$schema`, JSON Schema 2020-12 compatibility)
- [ ] Add OpenAPI version toggle (3.0 vs. 3.1 support via argument or config)
