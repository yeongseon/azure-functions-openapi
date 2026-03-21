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
