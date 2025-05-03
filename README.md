# azure-functions-openapi

**OpenAPI (Swagger) documentation generator for Python-based Azure Functions**

This library allows you to document your Azure Functions using decorators, and automatically exposes OpenAPI-compliant documentation (JSON and Swagger UI) without requiring an external framework.

---

## ✨ Features

- `@openapi` decorator to describe each Azure Function endpoint
- Auto-generated OpenAPI schema at `/openapi.json`
- Beautiful Swagger UI served at `/docs`
- Support for type hints and response models
- No need for Flask, FastAPI, or external web frameworks

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
    description="Returns a simple greeting message",
    response={200: {"description": "Successful response"}}
)
def main(req):
    return "Hello from Azure Functions!"
```

When deployed, your function app will expose:
- OpenAPI spec: `https://<your-func-app>.azurewebsites.net/openapi.json`
- Swagger UI: `https://<your-func-app>.azurewebsites.net/docs`

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
│   └── hello_world/
├── pyproject.toml
├── README.md
├── Makefile
├── .editorconfig
└── .gitignore
```

---

## 📄 License

MIT License © 2025 Yeongseon Choe
