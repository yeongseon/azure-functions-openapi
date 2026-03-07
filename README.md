# azure-functions-openapi

[![PyPI](https://img.shields.io/pypi/v/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-openapi/)
[![CI](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-openapi/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-openapi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-openapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OpenAPI (Swagger) documentation and Swagger UI for the **Azure Functions Python v2 programming model**.

## Scope

- Azure Functions Python **v2 programming model**
- Decorator-based `func.FunctionApp()` applications
- HTTP-triggered functions documented with `@openapi`
- Optional Pydantic schema generation (supports both Pydantic v1 and v2)

This package does **not** support the legacy `function.json`-based v1 programming model.

## Features

- `@openapi` decorator for operation metadata
- `/openapi.json`, `/openapi.yaml`, and `/docs` endpoints
- Query, path, header, body, and response schema support
- Swagger UI helper with security defaults
- CLI tooling for generation and validation workflows

## Demo

The CLI demo below is generated from [`demo/openapi-cli.tape`](demo/openapi-cli.tape) with VHS.

![OpenAPI CLI demo](docs/assets/openapi-cli-demo.gif)

## Installation

```bash
pip install azure-functions-openapi
```

Your Function App dependencies should include:

```text
azure-functions
azure-functions-openapi
```

## Quick Start

```python
import json

import azure.functions as func

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui


app = func.FunctionApp()


@app.function_name(name="http_trigger")
@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@openapi(
    summary="Greet user",
    route="/api/http_trigger",
    request_model={"name": "string"},
    response_model={"message": "string"},
    tags=["Example"],
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    name = data.get("name", "world")
    return func.HttpResponse(
        json.dumps({"message": f"Hello, {name}!"}),
        mimetype="application/json",
    )

@app.function_name(name="openapi_json")
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_json(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_json(
        title="Sample API",
        description="OpenAPI document for the Sample API.",
    )


@app.function_name(name="openapi_yaml")
@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_yaml(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_yaml(
        title="Sample API",
        description="OpenAPI document for the Sample API.",
    )


@app.function_name(name="swagger_ui")
@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

Run locally with Azure Functions Core Tools:

```bash
func start
```

## Documentation

- Full docs: [yeongseon.github.io/azure-functions-openapi](https://yeongseon.github.io/azure-functions-openapi/)
- Smoke-tested examples: `examples/`
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api.md)
- [CLI Guide](docs/cli.md)

## License

MIT
