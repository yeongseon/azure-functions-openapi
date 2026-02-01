# AGENT.md

Azure Functions Python Libraries – Standard Agent Rules (v1)

## 0. Purpose

This document defines **non-negotiable rules** for developing and maintaining this repository.

This project is developed using **AI-assisted “vibe coding”**, therefore:

* Consistency > flexibility
* Automation > memory
* Rules are enforced by tools, not humans

Any contribution (human or AI) **must follow this document**.

---

## 1. Repository Identity

* Project type: Python library for Azure Functions
* Runtime environment: Azure Functions (Python)
* Minimum supported Python: **3.10**
* Development Python: Latest stable (e.g. 3.12) is allowed
* Packaging: `pyproject.toml` (PEP 621)
* Build backend: Hatch

**Core rule**

Runtime compatibility is defined by the **minimum supported Python version (3.10)**.
Development may use newer Python versions, but **no runtime syntax, behavior, or typing
may exceed Python 3.10 compatibility**.

---

## 2. Golden Commands (Single Entry Points)

All development, CI, and debugging **must use Makefile commands only**.

| Purpose           | Command          |
| ----------------- | ---------------- |
| Environment setup | `make install`   |
| Code formatting   | `make format`    |
| Lint check        | `make lint`      |
| Type check        | `make typecheck` |
| Unit tests        | `make test`      |
| Coverage          | `make cov`       |
| Lint + type       | `make check`     |
| Full validation   | `make check-all` |
| Docs preview      | `make docs`      |
| Build package     | `make build`     |

❌ Do NOT call ruff / mypy / pytest directly
❌ Do NOT bypass the Makefile in CI

---

## 3. Minimum Python Version Discipline (Critical)

This repository supports **Python 3.10+**.

* You may develop using newer Python versions, but **all runtime code must remain compatible
  with Python 3.10**.
* Do not use Python 3.11/3.12-only syntax, stdlib APIs, or typing features in production code.

Examples (not exhaustive):

* ❌ `type X = ...` (Python 3.12)
* ❌ `except*` (Python 3.11)
* ❌ `tomllib` (Python 3.11) unless guarded or backported

CI must validate:

* tests on Python 3.10 (minimum)
* tests on latest supported Python

---

## 4. Code Style & Quality Rules

### Formatting & Linting

* Formatter: Ruff
* Linter: Ruff
* Rules are defined in `pyproject.toml`

### Type Checking

* Type checker: mypy
* Mode: strict
* All public APIs must be fully typed
* `# type: ignore` without justification is forbidden

### Testing

* Framework: pytest
* Public APIs must have tests
* Bug fixes must include regression tests

---

## 5. Error Logging & Exception Handling (Principles Only)

This repository is a **library**, not an application.

### Principles

* Do not swallow exceptions silently
* Prefer raising exceptions over logging-only behavior
* Log errors only when **additional context is added**
* Always preserve the original exception (exception chaining)

This library must not:

* Enforce a logging framework
* Decide log output format or destination

### Conceptual Log Structure

When logging an error, logs should conceptually include:

* event (stable identifier)
* error_type
* message
* context

Exact field names and APIs are intentionally not enforced.

---

## 6. Git & Commit Rules

* Conventional Commits are required

Format:

```
<type>: <short imperative summary>
```

Allowed types:
`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`

---

## 7. AI / Vibe Coding Rules (Critical)

When AI is used:

* Prefer small, incremental changes
* Do not introduce silent behavior changes
* Do not introduce untyped public APIs
* If uncertain, ask — do not guess

---

## 8. Consistency Across Repositories

This repository is part of a **multi-repository ecosystem**.

AGENT.md, tooling, CI structure, and documentation layout
**must remain consistent across all related repositories**.

Related docs: DESIGN.md, SUPPORT.md.

---

## Final Rule

If it is not automated, it does not exist.
If it is not documented here, it is not allowed.
