# Bridge Example

This example uses only `@validate_http` for runtime validation and lets
`scan_validation_metadata(app)` auto-generate OpenAPI documentation — no
`@openapi` decorator needed.

Source: `examples/with_bridge/function_app.py`

## Why this pattern is useful

With the bridge pattern you define Pydantic models **once** in `@validate_http`
and get both runtime validation and OpenAPI documentation automatically:

- `@validate_http(...)` → runtime parsing and validation
- `scan_validation_metadata(app)` → auto-registers models in the OpenAPI registry

No duplication between `@openapi` and `@validate_http` decorators.

## Endpoints

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/api/items` | Create item from validated JSON body |
| `GET` | `/api/items/{item_id}` | Get item with validated path params |
| `GET` | `/api/openapi.json` | OpenAPI JSON |
| `GET` | `/api/docs` | Swagger UI |

## Core models

```python
class CreateItemBody(BaseModel):
    name: str


class ItemPath(BaseModel):
    item_id: int


class ItemResponse(BaseModel):
    id: int
    name: str
```

## Complete example

```python
import json
import importlib
from typing import Any

import azure.functions as func
from pydantic import BaseModel

from azure_functions_openapi import scan_validation_metadata
from azure_functions_openapi.openapi import get_openapi_json
from azure_functions_openapi.swagger_ui import render_swagger_ui

validate_http = getattr(importlib.import_module("azure_functions_validation"), "validate_http")

app = func.FunctionApp()


class CreateItemBody(BaseModel):
    name: str


class ItemPath(BaseModel):
    item_id: int


class ItemResponse(BaseModel):
    id: int
    name: str


ITEMS: list[dict[str, Any]] = []


@app.function_name(name="create_item")
@app.route(route="items", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@validate_http(body=CreateItemBody, response_model=ItemResponse)
def create_item(req: func.HttpRequest, body: CreateItemBody) -> ItemResponse:
    item_id = len(ITEMS) + 1
    item = {"id": item_id, "name": body.name}
    ITEMS.append(item)
    return ItemResponse(id=item_id, name=body.name)


@app.function_name(name="get_item")
@app.route(route="items/{item_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@validate_http(path=ItemPath, response_model=ItemResponse)
def get_item(req: func.HttpRequest, path: ItemPath) -> func.HttpResponse:
    item = next((entry for entry in ITEMS if entry["id"] == path.item_id), None)
    if item is None:
        return func.HttpResponse("Not found", status_code=404)
    return func.HttpResponse(json.dumps(item), mimetype="application/json", status_code=200)


# Scan validation metadata and register in OpenAPI registry
scan_validation_metadata(app)


@app.function_name(name="openapi_spec")
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(title="Bridge Example"), mimetype="application/json")


@app.function_name(name="swagger_ui")
@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

## Key difference from `with_validation` example

| Pattern | `with_validation` | `with_bridge` |
| --- | --- | --- |
| Decorators | Both `@openapi` and `@validate_http` | Only `@validate_http` |
| Model declaration | Duplicated in both decorators | Declared once |
| Bridge call | Not needed | `scan_validation_metadata(app)` |
| Flexibility | Full OpenAPI control per endpoint | Auto-generated from validation |

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r examples/with_bridge/requirements.txt
func start
```

## Test with `curl`

### 1) Create item (valid)

```bash
curl -X POST "http://localhost:7071/api/items" \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget"}'
```

Expected output:

```json
{"id":1,"name":"Widget"}
```

### 2) Create item (invalid body)

```bash
curl -X POST "http://localhost:7071/api/items" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected behavior:

- request fails validation
- response status `422` with `{"detail": [...]}` envelope

### 3) Get item (valid)

```bash
curl "http://localhost:7071/api/items/1"
```

Expected output:

```json
{"id":1,"name":"Widget"}
```

### 4) Get unknown item

```bash
curl -i "http://localhost:7071/api/items/999"
```

Expected status:

```text
HTTP/1.1 404 Not Found
```

## Inspect generated docs

OpenAPI JSON:

```bash
curl "http://localhost:7071/api/openapi.json"
```

Swagger UI:

`http://localhost:7071/api/docs`

In Swagger UI, confirm:

- Both `POST /api/items` and `GET /api/items/{item_id}` are documented
- `CreateItemBody` appears as request schema for `POST`
- `ItemResponse` appears as response schema
- `item_id` path parameter is documented for `GET`

## Merge rules

When combining `@openapi` and `@validate_http` on the same handler:

- Explicit `@openapi` always takes precedence
- Same models: additional OpenAPI fields (summary, tags, etc.) are merged
- Different models: raises `OpenAPISpecConfigError`
- Only `@validate_http`: auto-registers with discovered models
- Only `@openapi`: existing behavior unchanged

## Related docs

- [With Validation Example](with_validation.md)
- [Usage](../usage.md)
- [API Reference](../api.md)
- [Installation](../installation.md)
