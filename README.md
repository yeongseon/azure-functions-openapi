# azure-functions-openapi

**OpenAPI (Swagger) documentation generator for Python-based Azure Functions**

This library allows you to document your Azure Functions using decorators, and automatically exposes OpenAPI-compliant documentation (`/openapi.json` and Swagger UI) without requiring an external framework.

---

## ✨ Features

- `@openapi` decorator to describe each Azure Function endpoint
- Auto-generated OpenAPI schema at `/openapi.json`
- Swagger UI served at `/swagger`
- Support for `parameters` (query/path/header) and `requestBody`
- Lightweight, no Flask or FastAPI required
- Easily extendable with `pydantic`, type hints, etc.

---

## 📦 Installation

```bash
pip install azure-functions-openapi
```

---

## 🚀 Quick Start

Example usage in `function_app.py`:

```python
from azure_functions_openapi import openapi

@openapi(
    summary="Say Hello",
    description="Returns a simple greeting",
    response={200: {"description": "Success"}},
    parameters=[
        {
            "name": "name",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Name to greet"
        }
    ],
    request_body={
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
)
def main(req):
    ...
```

When deployed, your Azure Function App will expose:

- OpenAPI spec: `https://<your-func-app>.azurewebsites.net/openapi.json`
- Swagger UI: `https://<your-func-app>.azurewebsites.net/swagger`

---

## 🧪 Development

```bash
make install        # Set up virtual environment and install dev dependencies
make check          # Run formatting, linting, type checking, and tests
```

---

## 📁 Project Structure

```
azure-functions-openapi/
├── src/
│   └── azure_functions_openapi/
├── tests/
├── examples/
│   └── openapi_json/
├── pyproject.toml
├── README.md
├── Makefile
├── .editorconfig
└── .gitignore
```

---

## 📄 License

MIT License © 2025 Yeongseon Choe
