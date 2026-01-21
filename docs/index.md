# Azure Functions OpenAPI

Welcome to **azure-functions-openapi** — a comprehensive library that provides seamless integration of **OpenAPI (Swagger)** documentation for Python-based Azure Functions with enterprise-grade security, performance, and monitoring capabilities.

## 🚀 Features

### Core Features
- **`@openapi` decorator** with comprehensive metadata support:
  - `summary`, `description`, `tags`
  - `operation_id`, `route`, `method`
  - `request_model`, `response_model`
  - `parameters`, `request_body`, `response`
- **Automatic generation** of:
  - `/openapi.json` - JSON specification
  - `/openapi.yaml` - YAML specification
  - `/docs` - Interactive Swagger UI
- **Pydantic v1 and v2 support** with automatic schema generation
- **Type-safe schema generation** with full type hints
- **Zero-configuration integration** - works out of the box
- **Compatible with Python 3.10+**

### 🔒 Security & Performance
- **Enhanced Security**: CSP headers, input validation, XSS protection
- **Performance Caching**: In-memory caching with TTL and LRU eviction
- **Error Handling**: Standardized error responses with detailed logging
- **Input Sanitization**: Automatic sanitization of routes, operation IDs, and parameters

### 📊 Monitoring & Operations
- **Health Checks**: Built-in health monitoring for all components
- **Performance Metrics**: Response time tracking, throughput monitoring
- **Request Logging**: Detailed request/response logging with statistics
- **Server Information**: Comprehensive server info and runtime details

### 🛠️ Developer Experience
- **CLI Tool**: Command-line interface for spec generation, validation, and monitoring
- **Comprehensive Testing**: 97% test coverage with extensive test suites
- **Documentation**: Detailed guides for security, performance, and CLI usage
- **Type Safety**: Full type hints and validation throughout

## Getting Started

### 1. Create a Function App and Register Routes

To expose your Azure Functions with OpenAPI documentation, decorate your function with `@openapi`
and register the documentation endpoints manually.

```python
# function_app.py

import json
import logging
import azure.functions as func
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui

app = func.FunctionApp()


@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    route="/api/http_trigger",
    summary="HTTP Trigger with name parameter",
    description="""
Returns a greeting using the **name** from query or body.

You can pass the name:
- via query string: `?name=Azure`
- via JSON body: `{ "name": "Azure" }`
""",
    operation_id="greetUser",
    tags=["Example"],
    parameters=[
        {
            "name": "name",
            "in": "query",
            "required": True,
            "schema": {"type": "string"},
            "description": "Name to greet",
        }
    ],
    response={
        200: {
            "description": "Successful response with greeting",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example greeting",
                            "value": {"message": "Hello, Azure!"},
                        }
                    }
                }
            },
        },
        400: {"description": "Invalid request"},
    },
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
            name = body.get("name") if isinstance(body, dict) else None
        except ValueError:
            pass

    if not name:
        return func.HttpResponse("Invalid request – `name` is required", status_code=400)

    return func.HttpResponse(
        json.dumps({"message": f"Hello, {name}!"}),
        mimetype="application/json",
        status_code=200,
    )


# OpenAPI documentation routes
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(), mimetype="application/json")


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml")


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

---

### 2. Run the App

Use the Azure Functions Core Tools:

```bash
func start
```

---

### 3. View the Swagger API

Once the app is running, open your browser:

- OpenAPI JSON: [http://localhost:7071/openapi.json](http://localhost:7071/openapi.json)
- OpenAPI YAML: [http://localhost:7071/openapi.yaml](http://localhost:7071/openapi.yaml)
- Swagger UI: [http://localhost:7071/docs](http://localhost:7071/docs)

---

## 📚 Documentation

### Getting Started
- [Quickstart Guide](./usage.md) - Get up and running quickly
- [Installation Guide](./installation.md) - Detailed installation instructions
- [API Reference](./api.md) - Complete API documentation

### Advanced Features
- [Security Guide](./SECURITY.md) - Security best practices and features
- [Performance Guide](./PERFORMANCE.md) - Performance optimization and monitoring
- [CLI Tool Guide](./CLI.md) - Command-line interface usage

### Examples & Tutorials
- [Hello OpenAPI Example](./examples/hello_openapi.md) - Basic example
- [Todo CRUD API Example](./examples/todo_crud_api.md) - Advanced example with Pydantic

### Development
- [Contribution Guide](./contributing.md) - How to contribute
- [Development Guide](./development.md) - Development setup and guidelines
- [Changelog](./changelog.md) - Version history and changes

---

## About

- Repository: [GitHub](https://github.com/yeongseon/azure-functions-openapi)
- License: MIT
