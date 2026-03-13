# Azure Functions OpenAPI

[![PyPI](https://img.shields.io/pypi/v/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-openapi/)
[![CI](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml)
[![Release](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/release.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/release.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-openapi/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-openapi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-openapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Read this in: [한국어](README.ko.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md)

OpenAPI (Swagger) documentation and Swagger UI for the **Azure Functions Python v2 programming model**.

## Why Use It

Documenting Azure Functions HTTP APIs typically requires maintaining a separate OpenAPI spec by hand. `azure-functions-openapi` generates the spec automatically from decorated handlers, keeping documentation and code in sync.

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
    method="post",
    request_body={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
    response={
        200: {
            "description": "Successful greeting",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        }
    },
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

## Demo

The representative `hello` example shows the full outcome of adopting this library:

- You annotate an Azure Functions v2 HTTP handler with `@openapi`.
- The package generates a real OpenAPI document for that route.
- The same route is rendered in Swagger UI for browser-based inspection.

### Generated Spec Result

The generated OpenAPI file is captured as a static preview from the same example run, so the README shows the actual document produced by the representative function.

![OpenAPI spec preview](docs/assets/hello_openapi_spec_preview.png)

### Swagger UI Result

The web preview below is generated from the same representative example and captured automatically from the rendered Swagger UI page produced by that example flow.

![OpenAPI Swagger UI preview](docs/assets/hello_openapi_swagger_ui_preview.png)

## Documentation

- Full docs: [yeongseon.github.io/azure-functions-openapi](https://yeongseon.github.io/azure-functions-openapi/)
- Smoke-tested examples: `examples/`
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api.md)
- [CLI Guide](docs/cli.md)

## Ecosystem

- [azure-functions-validation](https://github.com/yeongseon/azure-functions-validation) — Request and response validation
- [azure-functions-logging](https://github.com/yeongseon/azure-functions-logging) — Structured logging
- [azure-functions-doctor](https://github.com/yeongseon/azure-functions-doctor) — Diagnostic CLI
- [azure-functions-scaffold](https://github.com/yeongseon/azure-functions-scaffold) — Project scaffolding
- [azure-functions-python-cookbook](https://github.com/yeongseon/azure-functions-python-cookbook) — Recipes and examples

## Disclaimer

This project is an independent community project and is not affiliated with,
endorsed by, or maintained by Microsoft.

Azure and Azure Functions are trademarks of Microsoft Corporation.

## License

MIT
