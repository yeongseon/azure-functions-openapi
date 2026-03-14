# API Reference

This page documents the public runtime API exposed by `azure-functions-openapi`.

!!! info "Import from package root"
    All symbols below are exported from `azure_functions_openapi.__init__`, so you can import from `azure_functions_openapi` directly.

```python
from azure_functions_openapi import (
    OPENAPI_VERSION_3_0,
    OPENAPI_VERSION_3_1,
    generate_openapi_spec,
    get_openapi_json,
    get_openapi_yaml,
    openapi,
    render_swagger_ui,
)
```

## Public API surface

| Symbol | Kind | Purpose |
| --- | --- | --- |
| `openapi` | decorator | Attach operation metadata to function handlers |
| `generate_openapi_spec` | function | Build OpenAPI dictionary from decorator registry |
| `get_openapi_json` | function | Build OpenAPI and serialize to JSON string |
| `get_openapi_yaml` | function | Build OpenAPI and serialize to YAML string |
| `render_swagger_ui` | function | Return Swagger UI `HttpResponse` |
| `OPENAPI_VERSION_3_0` | constant | OpenAPI version string `"3.0.0"` |
| `OPENAPI_VERSION_3_1` | constant | OpenAPI version string `"3.1.0"` |

## Decorator behavior model

`@openapi` stores metadata in a thread-safe registry and the spec functions read from that registry to generate output.

```text
@openapi metadata -> internal registry -> generate_openapi_spec -> JSON/YAML endpoint
                                                    -> render_swagger_ui (browser docs)
```

!!! note
    `get_openapi_json()` and `get_openapi_yaml()` return strings, not `HttpResponse`. Wrap the returned value in `func.HttpResponse` in your Azure Function route.

## Common usage patterns

### Minimal endpoint

```python
@app.route(route="ping", methods=["GET"])
@openapi(summary="Ping", description="Health check endpoint")
def ping(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("ok", status_code=200)
```

### With Pydantic request and response

```python
class CreateItemRequest(BaseModel):
    name: str


class ItemResponse(BaseModel):
    id: int
    name: str


@app.route(route="items", methods=["POST"])
@openapi(
    summary="Create item",
    method="post",
    route="/api/items",
    request_model=CreateItemRequest,
    response_model=ItemResponse,
    response={201: {"description": "Created"}},
)
def create_item(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

### With raw schema dictionaries

```python
@app.route(route="raw", methods=["POST"])
@openapi(
    summary="Raw schema example",
    method="post",
    request_body={
        "type": "object",
        "properties": {"value": {"type": "string"}},
        "required": ["value"],
    },
    response={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"accepted": {"type": "boolean"}},
                    }
                }
            },
        }
    },
)
def raw(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

### Expose OpenAPI + Swagger routes

```python
@app.route(route="openapi.json", methods=["GET"])
def openapi_json(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(title="My API", version="1.0.0"), mimetype="application/json")


@app.route(route="openapi.yaml", methods=["GET"])
def openapi_yaml(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_yaml(title="My API", version="1.0.0"), mimetype="application/x-yaml")


@app.route(route="docs", methods=["GET"])
def docs(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui(title="My API Docs", openapi_url="/api/openapi.json")
```

## mkdocstrings reference

The sections below are generated directly from source docstrings.

### `openapi`

::: azure_functions_openapi.openapi

### `generate_openapi_spec`

::: azure_functions_openapi.generate_openapi_spec

### `get_openapi_json`

::: azure_functions_openapi.get_openapi_json

### `get_openapi_yaml`

::: azure_functions_openapi.get_openapi_yaml

### `render_swagger_ui`

::: azure_functions_openapi.render_swagger_ui

## Related internals

While not part of the top-level runtime import list for app code, these internals are useful when debugging:

- Registry accessor: `azure_functions_openapi.decorator.get_openapi_registry`
- Route sanitizer: `azure_functions_openapi.utils.validate_route_path`
- Operation ID sanitizer: `azure_functions_openapi.utils.sanitize_operation_id`

## Version constants

Use these constants for explicit version selection:

```python
from azure_functions_openapi import OPENAPI_VERSION_3_0, OPENAPI_VERSION_3_1

spec_30 = get_openapi_json(openapi_version=OPENAPI_VERSION_3_0)
spec_31 = get_openapi_json(openapi_version=OPENAPI_VERSION_3_1)
```

!!! tip
    Prefer constants over hardcoded strings to avoid typos and keep version intent explicit in code review.

## Cross-links

- [Usage Guide](usage.md)
- [Configuration](configuration.md)
- [CLI](cli.md)
- [Architecture](architecture.md)
- [Troubleshooting](troubleshooting.md)
