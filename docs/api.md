# API Reference

This document provides the complete API reference for `azure-functions-openapi`.

## Public API

All public symbols are re-exported from the top-level package:

```python
from azure_functions_openapi import (
    openapi,
    generate_openapi_spec,
    get_openapi_json,
    get_openapi_yaml,
    render_swagger_ui,
    OPENAPI_VERSION_3_0,
    OPENAPI_VERSION_3_1,
)
```

---

## `@openapi` Decorator

```python
azure_functions_openapi.decorator.openapi(
    summary: str = "",
    description: str = "",
    tags: list[str] | None = None,
    operation_id: str | None = None,
    route: str | None = None,
    method: str | None = None,
    parameters: list[dict[str, Any]] | None = None,
    security: list[dict[str, list[str]]] | None = None,
    security_scheme: dict[str, dict[str, Any]] | None = None,
    request_model: type[BaseModel] | None = None,
    request_body: dict[str, Any] | None = None,
    response_model: type[BaseModel] | None = None,
    response: dict[int, dict[str, Any]] | None = None,
) -> Callable[[F], F]
```

Attaches OpenAPI metadata to an Azure Functions HTTP handler. The metadata is stored
in a thread-safe global registry and consumed at spec-generation time.

### Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `summary` | `str` | `""` | Short summary displayed in Swagger UI. |
| `description` | `str` | `""` | Longer description; supports Markdown (CommonMark). |
| `tags` | `list[str] \| None` | `None` | Group tags for organizing endpoints. Defaults to `["default"]` when omitted. |
| `operation_id` | `str \| None` | `None` | Custom `operationId`. Defaults to `{method}_{function_name}`. Must match `^[a-zA-Z][a-zA-Z0-9_]*$`. |
| `route` | `str \| None` | `None` | Override for the HTTP path in the spec (e.g., `/api/items/{id}`). Must not contain whitespace or path-traversal sequences. |
| `method` | `str \| None` | `None` | Explicit HTTP method. Defaults to `"get"` if not inferrable. |
| `parameters` | `list[dict]` | `None` | OpenAPI Parameter Objects for `query`, `path`, `header`, or `cookie` parameters. |
| `security` | `list[dict]` | `None` | OpenAPI Security Requirement Objects (e.g., `[{"BearerAuth": []}]`). |
| `security_scheme` | `dict` | `None` | Security scheme definitions for `components.securitySchemes`. |
| `request_model` | `type[BaseModel]` | `None` | Pydantic model class for the request body. Schema is derived automatically. |
| `request_body` | `dict` | `None` | Raw request body schema dict. Use this when not using Pydantic. |
| `response_model` | `type[BaseModel]` | `None` | Pydantic model class for the 200 response body. |
| `response` | `dict[int, dict]` | `None` | Response definitions keyed by HTTP status code. |

### Raises

- `ValueError` -- Invalid route path, operation ID, parameters, security definition, or model type.
- `TypeError` -- Decorated object is not callable and not a `FunctionBuilder`.
- `RuntimeError` -- Unexpected error during metadata registration.

### Example: Minimal

```python
@app.route(route="hello", methods=["GET"])
@openapi(summary="Hello endpoint", route="/api/hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, world!")
```

### Example: Full Parameters

```python
@app.route(route="todos/{id}", methods=["PUT"])
@openapi(
    summary="Update a todo",
    description="Replace a todo item by ID.",
    tags=["Todos"],
    operation_id="updateTodo",
    route="/api/todos/{id}",
    method="put",
    parameters=[
        {
            "name": "id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
        },
        {
            "name": "X-Request-ID",
            "in": "header",
            "required": False,
            "schema": {"type": "string"},
        },
    ],
    security=[{"BearerAuth": []}],
    security_scheme={
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
    request_model=TodoUpdateRequest,
    response_model=TodoResponse,
    response={
        200: {"description": "Todo updated"},
        400: {"description": "Invalid request"},
        404: {"description": "Todo not found"},
    },
)
def update_todo(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

---

## `get_openapi_registry()`

```python
azure_functions_openapi.decorator.get_openapi_registry() -> dict[str, dict[str, Any]]
```

Returns a snapshot of the global OpenAPI metadata registry. Each key is a function
name and the value is a dictionary of OpenAPI metadata fields.

This function acquires the registry lock and returns copies of the stored metadata.

### Returns

`dict[str, dict[str, Any]]` -- A dictionary mapping function names to their OpenAPI metadata.

---

## `generate_openapi_spec()`

```python
azure_functions_openapi.openapi.generate_openapi_spec(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = "3.0.0",
    description: str = "Auto-generated OpenAPI documentation. ...",
    security_schemes: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]
```

Compiles the full OpenAPI specification from the metadata registry.

### Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | `str` | `"API"` | The `info.title` field. |
| `version` | `str` | `"1.0.0"` | The `info.version` field. |
| `openapi_version` | `str` | `"3.0.0"` | OpenAPI specification version (`"3.0.0"` or `"3.1.0"`). |
| `description` | `str` | *(auto-generated)* | The `info.description` field. Supports Markdown. |
| `security_schemes` | `dict \| None` | `None` | Central security scheme definitions for `components.securitySchemes`. |

### Returns

`dict[str, Any]` -- The complete OpenAPI specification as a dictionary.

### Raises

- `ValueError` -- Unsupported `openapi_version`.
- `RuntimeError` -- Failed to generate the specification.

### Behavior

1. Iterates over all entries in the global registry.
2. Builds `paths` from route and method metadata.
3. Derives request/response schemas from Pydantic models or raw dicts.
4. Merges security schemes from both central definitions and per-decorator definitions.
5. For OpenAPI 3.1, converts `nullable` to type arrays and `example` to `examples`.

---

## `get_openapi_json()`

```python
azure_functions_openapi.openapi.get_openapi_json(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = "3.0.0",
    description: str = "Auto-generated OpenAPI documentation. ...",
    security_schemes: dict[str, dict[str, Any]] | None = None,
) -> str
```

Returns the OpenAPI specification as pretty-printed JSON (UTF-8).

### Parameters

Same as `generate_openapi_spec()`.

### Returns

`str` -- JSON string with 2-space indentation.

### Example

```python
@app.route(route="openapi.json", methods=["GET"])
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    body = get_openapi_json(
        title="My API",
        version="2.0.0",
        description="My API description.",
    )
    return func.HttpResponse(body, mimetype="application/json")
```

---

## `get_openapi_yaml()`

```python
azure_functions_openapi.openapi.get_openapi_yaml(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = "3.0.0",
    description: str = "Auto-generated OpenAPI documentation. ...",
    security_schemes: dict[str, dict[str, Any]] | None = None,
) -> str
```

Returns the OpenAPI specification as YAML.

### Parameters

Same as `generate_openapi_spec()`.

### Returns

`str` -- YAML string produced by `yaml.safe_dump()`.

### Example

```python
@app.route(route="openapi.yaml", methods=["GET"])
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    body = get_openapi_yaml(title="My API", version="2.0.0")
    return func.HttpResponse(body, mimetype="application/x-yaml")
```

---

## `render_swagger_ui()`

```python
azure_functions_openapi.swagger_ui.render_swagger_ui(
    title: str = "API Documentation",
    openapi_url: str = "/api/openapi.json",
    custom_csp: str | None = None,
    enable_client_logging: bool = False,
) -> HttpResponse
```

Renders the Swagger UI as an Azure Functions `HttpResponse` with security headers.

### Parameters

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | `str` | `"API Documentation"` | Page title for the Swagger UI HTML. |
| `openapi_url` | `str` | `"/api/openapi.json"` | URL to the OpenAPI specification endpoint. |
| `custom_csp` | `str \| None` | `None` | Custom Content Security Policy. When `None`, a restrictive default CSP is applied. |
| `enable_client_logging` | `bool` | `False` | When `True`, logs API response status and URL to the browser console. |

### Returns

`HttpResponse` -- HTML response with the following security headers:

| Header | Value |
| --- | --- |
| `Content-Security-Policy` | Restrictive default or custom CSP |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Cache-Control` | `no-cache, no-store, must-revalidate` |

### Example

```python
@app.route(route="docs", methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui(
        title="My API Docs",
        openapi_url="/api/openapi.json",
    )
```

---

## Constants

### `OPENAPI_VERSION_3_0`

```python
OPENAPI_VERSION_3_0 = "3.0.0"
```

### `OPENAPI_VERSION_3_1`

```python
OPENAPI_VERSION_3_1 = "3.1.0"
```

Pass these to `generate_openapi_spec()`, `get_openapi_json()`, or `get_openapi_yaml()`
to select the output specification version.

---

## Utility Functions

These are internal utilities but are documented for contributors.

### `model_to_schema()`

```python
azure_functions_openapi.utils.model_to_schema(
    model_cls: Any,
    components: dict[str, Any] | None = None,
) -> dict[str, Any]
```

Converts a Pydantic `BaseModel` class to an OpenAPI-compatible JSON schema reference.
Handles both Pydantic v1 and v2. Nested model definitions are extracted into
`components.schemas` and referenced via `$ref`.

### `validate_route_path()`

```python
azure_functions_openapi.utils.validate_route_path(route: Any) -> bool
```

Returns `True` if the route path is safe. Rejects path traversal (`..`), script
injection, `javascript:` URIs, and whitespace.

### `sanitize_operation_id()`

```python
azure_functions_openapi.utils.sanitize_operation_id(operation_id: Any) -> str
```

Strips non-alphanumeric characters (except underscores) and ensures the result starts
with a letter. Returns an empty string for invalid input.
