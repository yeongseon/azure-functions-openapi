# AGENTS.md

## Purpose
`azure-functions-openapi` provides OpenAPI generation and validation support for Python Azure Functions.

## Read First
- `README.md`
- `CONTRIBUTING.md`
- `docs/agent-playbook.md`

## Working Rules
- Preserve the package's Python compatibility and public CLI behavior unless the change explicitly updates the contract.
- Keep documentation examples, generated schema expectations, and tests synchronized.
- Prefer focused changes inside the existing extension points.

## Validation
- `make test`
- `make lint`
- `make typecheck`
- `make build`

## Release Process
- Version is managed via `hatch` (dynamic from `src/azure_functions_openapi/__init__.py`).
- **Do NOT manually edit version strings.** Use the Makefile targets below.
- When bumping version, update `tests/test_public_api.py` to match the new version string.

### Commands
- `make release-patch` — bump patch version, update changelog, tag, and push
- `make release-minor` — bump minor version, update changelog, tag, and push
- `make release-major` — bump major version, update changelog, tag, and push
- `make release VERSION=x.y.z` — set explicit version, update changelog, tag, and push
- `make tag-release VERSION=x.y.z` — create and push an annotated tag (used internally by release targets)

### Flow
1. `make release-patch` (or `-minor` / `-major`) on `main`
2. This runs: `hatch version` → `git commit` → `make changelog` → `git commit` → `git tag` → `git push`
3. Tag push triggers **Publish to PyPI** GitHub Actions workflow automatically.
4. Update `docs/changelog.md` separately if needed (different format from `CHANGELOG.md`).
