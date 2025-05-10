# Azure Functions OpenAPI

Welcome to **azure-functions-openapi** — a library that provides seamless integration of **OpenAPI (Swagger)** documentation for Python-based Azure Functions.

## ✨ Features

- `@openapi` decorator with `summary`, `description`, `tags`, `request_model`, `response_model`
- Automatic generation of:
  - `/openapi.json`
  - `/openapi.yaml`
  - `/docs` (Swagger UI)
- Pydantic-based schema validation and generation
- Lightweight and fully compatible with Azure Functions Python Programming Model v2

## 🚀 Getting Started

Install the package:

```bash
pip install azure-functions-openapi
```

Decorate your function:

```python
@openapi(
    summary="Say Hello",
    description="Returns a greeting message.",
    response_model=HelloResponse
)
def hello(req: HttpRequest) -> HttpResponse:
    ...
```

## 📚 Documentation

- [Quickstart](./usage.md)
- [Installation Guide](./installation.md)
- [API Reference](./api.md)
- [Examples](./examples/hello_openapi.md)
- [Contribution Guide](./contributing.md)
- [Development Guide](./development.md)

---

## 🛠 About

- Repository: [GitHub](https://github.com/yeongseon/azure-functions-openapi)
- License: MIT

Enjoy building well-documented serverless APIs! 🚀
