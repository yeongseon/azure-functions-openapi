# Architecture

This document explains how `azure-functions-openapi-python` transforms decorator metadata into OpenAPI output and Swagger UI responses.

## High-level design

```text
Function handlers + @openapi metadata
            |
            v
Thread-safe metadata registry (decorator.py)
            |
            v
Spec compiler (openapi.py)
   |                     |
   v                     v
JSON / YAML strings      Swagger UI HTML response (swagger_ui.py)
```

## Core modules

## `decorator.py`

Responsibilities:

- provide `@openapi(...)`
- validate and sanitize decorator inputs
- store operation metadata in `_openapi_registry`
- expose `get_openapi_registry()` snapshot accessor

Key behaviors:

- registry writes are protected by `threading.RLock`
- tags default to `['default']` when not provided
- invalid route path or operation ID raises `ValueError`

## `openapi.py`

Responsibilities:

- compile registry into OpenAPI document (`generate_openapi_spec`)
- serialize to JSON (`get_openapi_json`) and YAML (`get_openapi_yaml`)
- support OpenAPI 3.0.0 and 3.1.0 output

Spec generation flow:

1. Read registry entries
2. Resolve route and method per operation
3. Build responses and request body schemas
4. Convert Pydantic models into `components.schemas`
5. Merge security schemes (global + per-operation)
6. Return final `spec` dictionary

3.1-specific conversion:

- `nullable: true` -> `type: ["<type>", "null"]`
- `example` -> `examples`

## `utils.py`

Responsibilities:

- Pydantic v2 schema extraction (`model_to_schema`)
- `$ref` rewriting to `#/components/schemas/...`
- schema collision resolution for repeated model names
- route and operation ID validation helpers

Important details:

- nested `$defs`/`definitions` are collected recursively
- colliding schema names are suffixed (`_2`, `_3`, ...)

## `swagger_ui.py`

Responsibilities:

- render Swagger UI HTML via `render_swagger_ui`
- apply security headers
- sanitize title and URL inputs

Headers added include:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- cache prevention headers

## `cli.py`

Responsibilities:

- parse `azure-functions-openapi-python generate` command
- output JSON/YAML to stdout or file
- choose OpenAPI version (`3.0` or `3.1`)

## Request lifecycle perspective

At startup:

1. Python imports function modules
2. `@openapi` executes and registers metadata

At spec request time (`/api/openapi.json` or `/api/openapi.yaml`):

1. endpoint function calls `get_openapi_json()` or `get_openapi_yaml()`
2. generator compiles current registry
3. endpoint wraps returned string in `func.HttpResponse`

At docs request time (`/api/docs`):

1. endpoint calls `render_swagger_ui(openapi_url=...)`
2. HTML + security headers are returned
3. browser fetches OpenAPI document from `openapi_url`

## Design constraints

- no function source parsing; metadata is runtime-decorator driven
- no persistence layer; registry exists in process memory
- assumes module import/registration has already happened

## Operational considerations

- missing imports can lead to empty `paths`
- inconsistent `@app.route` vs `@openapi(route=...)` leads to doc/runtime mismatch
- model schema generation is resilient but invalid model usage raises explicit errors

## Extension points

- customize spec metadata via generator arguments (`title`, `version`, `description`)
- configure security centrally (`security_schemes`) or per operation (`security_scheme`)
- customize UI CSP and behavior via `render_swagger_ui(...)`

## Related docs

- [Usage](usage.md)
- [Configuration](configuration.md)
- [API Reference](api.md)
- [Troubleshooting](troubleshooting.md)
