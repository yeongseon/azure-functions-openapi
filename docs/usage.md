# Usage Guide: azure-functions-openapi

This guide walks you through using the `azure-functions-openapi` library to document your Azure Functions using OpenAPI (Swagger) specifications.

---

## 1. Getting Started

### Install the package

```bash
pip install azure-functions-openapi
```

For development version:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .
```

### Folder Structure

```
azure-functions-openapi/
├── src/
├── tests/
├── examples/
├── docs/
```

---

## 2. `@openapi` Decorator

Use `@openapi` to annotate your Azure Function.

### Supported Arguments:

| Argument       | Type               | Description |
|----------------|--------------------|-------------|
| `summary`      | `str`              | One-line summary |
| `description`  | `str`              | Supports **Markdown** |
| `response`     | `dict`             | HTTP status code to response spec |
| `parameters`   | `list`             | Query, path, header, or cookie params |
| `request_model`| `BaseModel`        | Auto-generate request body schema |
| `response_model`| `BaseModel`       | Auto-generate response schema |
| `tags`         | `list[str]`        | Group endpoints |
| `operation_id` | `str`              | Custom unique identifier |
| `route`        | `str`              | Override the default path |
| `method`       | `str`              | GET/POST/PUT/... |

---

## 3. Models with Pydantic

```python
from pydantic import BaseModel

class RequestModel(BaseModel):
    username: str
    age: int

class ResponseModel(BaseModel):
    message: str
```

These models generate accurate schema definitions in the OpenAPI spec.

---

## 4. Parameters (query/path/header/cookie)

```python
parameters=[
    {
        "name": "q",
        "in": "query",  # or path, header, cookie
        "required": False,
        "schema": {"type": "string"},
        "description": "Search query string"
    }
]
```

All types except `cookie` are fully supported. `cookie` support is in progress.

---

## 5. OpenAPI 3.0 vs 3.1

- Currently: **OpenAPI 3.0**
- Planned:
  - Nullable types
  - `oneOf`, `anyOf`, `const` improvements
  - JSON Schema 2020-12 support

---

## 6. Swagger UI Customization

You can override the `swagger_ui()` function and add:

```html
<link rel="stylesheet" href="https://your-domain/custom.css">
<script src="https://your-domain/custom.js"></script>
```

Customize `SwaggerUIBundle({...})` as needed.

---

## 7. JSON and YAML output

- `/openapi.json` – Default JSON spec
- `/openapi.yaml` – Human-readable YAML (requires `PyYAML`)

These can be imported into:

- Postman
- SwaggerHub
- Azure API Management

---

## Example Function

```python
@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Greet user",
    description="Returns a greeting.\n\n### Usage\nPass `name` in query or body.",
    request_model=RequestModel,
    response_model=ResponseModel,
    tags=["Example"],
    operation_id="greetUser"
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

---

## Docs Endpoints

| Endpoint         | Description                |
|------------------|----------------------------|
| `/swagger`       | Swagger UI                 |
| `/openapi.json`  | OpenAPI in JSON            |
| `/openapi.yaml`  | OpenAPI in YAML (if enabled) |
