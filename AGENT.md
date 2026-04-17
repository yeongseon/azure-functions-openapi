# AGENT.md

Azure Functions Python Libraries - Repository Rules

## Purpose

This document defines the repository-level rules for contributors and coding agents.

This repository is part of a multi-project Azure Functions Python ecosystem, so automation,
structure, and terminology must stay aligned across repositories.

## Repository Identity

- Project: `azure-functions-openapi-python`
- Project type: Python library
- Runtime scope: Azure Functions Python v2 programming model
- Minimum supported Python: `3.10`
- Packaging: `pyproject.toml` with Hatch

## Root vs Docs

Use the repository root for engineering and planning documents:

- `AGENT.md`: contribution and automation rules
- `DESIGN.md`: architecture and design principles
- `PRD.md`: product scope and user-facing goals

Use `docs/` for user-facing documentation only:

- installation
- usage
- API reference
- examples
- diagnostics and guides

If a change materially affects behavior, architecture, or project positioning, update the
relevant root document in the same pull request or commit series.

## Golden Commands

Use Makefile entry points only.

| Purpose | Command |
| --- | --- |
| Environment setup | `make install` |
| Format code | `make format` |
| Lint | `make lint` |
| Type check | `make typecheck` |
| Tests | `make test` |
| Coverage | `make cov` |
| Full validation | `make check-all` |
| Docs build | `make docs` |
| Package build | `make build` |

Do not bypass the Makefile in CI or contributor guidance.

## Compatibility Rules

- Runtime code must remain compatible with Python `3.10`.
- Public APIs must be fully typed.
- Avoid silent behavior changes.
- Breaking changes require explicit documentation and versioning discussion.

## Testing Rules

- Public APIs require tests.
- Bug fixes require regression tests.
- Representative and complex examples must remain smoke-tested.
- `make check-all` is the minimum merge gate.

## Commit Rules

Use Conventional Commits:

```text
<type>: <short imperative summary>
```

Allowed types:
`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`

## Agent Rules

When using AI-assisted development:

- Prefer small, reviewable changes.
- Do not guess about behavior that can be verified.
- Keep repository structure aligned with sibling repositories.
- Update docs, examples, and tests together when behavior changes.

## Final Rule

If it is not automated, it will drift.
If it is not documented, it is not a stable rule.
