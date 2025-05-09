# Usage Guide: azure-functions-openapi

This guide walks you through documenting your Python Azure Functions with **OpenAPI (Swagger)** using `azure-functions-openapi`.

---

## 1. Getting Started

### Install

```bash
pip install azure-functions-openapi
```

For the development version:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .
```

### Folder Snapshot

```
azure-functions-openapi/
├── src/
├── tests/
├── examples/
└── docs/
```

---

## 2. `@openapi` Decorator

Annotate each function with `@openapi` and the library will register metadata for the spec builder.

### Supported Arguments

| Argument         | Type        | Description                                                       |
|------------------|-------------|-------------------------------------------------------------------|
| `summary`        | `str`       | One‑line summary                                                  |
| `description`    | `str`       | Markdown description                                              |
| `tags`           | `list[str]` | Tag list to group the endpoint                                    |
| `operation_id`   | `str`       | Custom unique identifier                                          |
| `route`          | `str`       | Override default path (e.g. `/users/{id}`)                        |
| `method`         | `str`       | HTTP verb (`GET`, `POST`, `PUT`, …)                               |
| `parameters`     | `list`      | Query, path, header or cookie parameters                          |
| `request_model`  | `BaseModel` | Pydantic model → requestBody schema                               |
| `request_body`   | `dict`      | Manual requestBody schema (use when not relying on a model)       |
| `response_model` | `BaseModel` | Pydantic model → 200‑response schema                              |
| `response`       | `dict`      | Manual responses keyed by HTTP status code                        |

---

## 3. Models with Pydantic (v2 only)

> **Note**  `azure-functions-openapi` targets **Pydantic v2**. Older v1 models are not supported.

```python
from pydantic import BaseModel

class RequestModel(BaseModel):
    username: str
    age: int

class ResponseModel(BaseModel):
    message: str
```

These classes are converted into JSON‑schema and injected under `components/schemas`.

---

## 4. Parameters (query / path / header / cookie)

```python
parameters = [
    {
        "name": "q",
        "in": "query",  # path, header, or cookie also allowed
        "required": False,
        "schema": {"type": "string"},
        "description": "Search query string",
    }
]
```

All types except **`cookie`** are fully supported today (cookie support is on the roadmap).

---

## 5. OpenAPI 3.0 vs 3.1

| Status     | Notes                                                        |
|------------|--------------------------------------------------------------|
| **3.0** ✔  | Current output                                              |
| **3.1** ⏳ | Planned: nullable, `oneOf`/`anyOf`/`const`, JSON Schema 2020‑12 |

---

## 6. Docs (Swagger UI) Customization

Override `swagger_ui()` in your project to inject custom assets:

```html
<link rel="stylesheet" href="https://example.com/custom.css">
<script src="https://example.com/custom.js"></script>
```

Inside the HTML you can tweak the `SwaggerUIBundle({ ... })` options.

---

## 7. JSON & YAML Endpoints

| Endpoint        | Purpose                         |
|-----------------|---------------------------------|
| `/docs`         | Interactive Swagger UI          |
| `/openapi.json` | Raw spec (JSON)                 |
| `/openapi.yaml` | Raw spec (YAML, requires PyYAML) |

These outputs import directly into Postman, SwaggerHub, Azure API Management, etc.

---

## Example Function

```python
@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Greet user",
    description="""Returns a greeting.

### Usage

Pass `name` in query or body.""",
    request_model=RequestModel,
    response_model=ResponseModel,
    tags=["Example"],
    operation_id="greetUser",
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

---

Happy documenting! 🚀
