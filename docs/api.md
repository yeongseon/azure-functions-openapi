# API Reference

This document provides comprehensive API reference for the azure-functions-openapi library.

## Table of Contents

- Core Components
- OpenAPI Helpers
- Swagger UI
- Server Info and Health
- CLI Commands

## Core Components

### `@openapi` Decorator

The `@openapi` decorator attaches OpenAPI metadata to an Azure Function route.
This metadata is collected to generate the OpenAPI spec using `get_openapi_json()` and `get_openapi_yaml()`.

### Error Handling

The library provides comprehensive error handling with standardized error responses:

```python
from azure_functions_openapi.errors import (
    APIError, ValidationError, NotFoundError, OpenAPIError,
    create_error_response, handle_exception
)
```

### Caching System

High-performance caching with TTL and LRU eviction:

```python
from azure_functions_openapi.cache import (
    cached, get_cache_manager, invalidate_cache, clear_all_cache
)
```

### Monitoring & Health Checks

Built-in monitoring and health check capabilities:

```python
from azure_functions_openapi.monitoring import (
    monitor_performance, log_request, run_health_check
)
from azure_functions_openapi.server_info import get_server_info_dict
```

---

## OpenAPI Helpers

```python
from azure_functions_openapi.openapi import (
    generate_openapi_spec,
    get_openapi_json,
    get_openapi_yaml,
)
```

Use these helpers to generate the OpenAPI spec directly for custom endpoints
or offline workflows.

## Swagger UI

```python
from azure_functions_openapi.swagger_ui import render_swagger_ui
```

`render_swagger_ui()` returns an `HttpResponse` with security headers and the
Swagger UI HTML.

## Server Info and Health

```python
from azure_functions_openapi.server_info import (
    get_server_info_dict,
    get_health_status,
    get_metrics,
)
```

These helpers provide runtime details, health status, and performance metrics
for monitoring endpoints.

## CLI Commands

The CLI exposes:

- `generate` for OpenAPI spec generation
- `info` for server info
- `health` for health checks
- `metrics` for performance metrics
- `validate` for OpenAPI spec validation

---

## Parameters

| Name            | Type         | Description                                               |
|-----------------|--------------|-----------------------------------------------------------|
| summary         | str          | Short summary shown in Swagger UI                         |
| description     | str          | Long description in Markdown                              |
| request_model   | BaseModel    | Pydantic model for request body (auto schema)             |
| request_body    | dict         | Manual schema for request body (if not using a model)     |
| response_model  | BaseModel    | Pydantic model for response body (200 by default)         |
| response        | dict         | Custom response object with status codes and examples     |
| tags            | List[str]    | Group endpoints under tags in Swagger UI                  |
| operation_id    | str          | Unique identifier for the operation                       |
| route           | str          | Optional override for the HTTP path in spec               |
| method          | str          | Optional override for the HTTP method in spec             |
| parameters      | list         | Query, path, header, or cookie parameters                 |

---

## Complete Example (GET)

```python
@openapi(
    summary="Get a todo by ID",
    description="""
Retrieve a single todo item by its ID, passed via query string.

Supports optional header `X-Request-ID` for tracing.
""",
    tags=["Todos"],
    operation_id="getTodo",
    route="/api/get_todo",
    method="get",
    parameters=[
        {
            "name": "id",
            "in": "query",
            "required": True,
            "description": "ID of the todo item",
            "schema": {"type": "integer"}
        },
        {
            "name": "X-Request-ID",
            "in": "header",
            "required": False,
            "description": "Optional request ID for logging",
            "schema": {"type": "string"}
        }
    ],
    request_model=None,
    request_body=None,
    response_model=TodoResponse,
    response={
        200: {"description": "Todo item returned"},
        400: {"description": "Invalid ID"},
        404: {"description": "Todo not found"}
    }
)
```

This example demonstrates:
- `query` parameter for the `id`
- `header` parameter for an optional custom header
- `response_model` for typed 200 response
- `response` for full control over status codes

---

## Notes

- `parameters` follow the OpenAPI spec format and support `query`, `path`, `header`, and (planned) `cookie`.
- You can mix `response_model` with manual `response` for extended behavior.
- All metadata is stored and rendered dynamically at runtime via the registry.
