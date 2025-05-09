# azure-functions-openapi

[![PyPI](https://img.shields.io/pypi/v/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![Python Version](https://img.shields.io/pypi/pyversions/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![CI](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-openapi/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-openapi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-openapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **azure-functions-openapi** – effortless OpenAPI ( Swagger ) documentation & Swagger‑UI for **Python Azure Functions**.

---

## Features

- **`@openapi` decorator** – annotate each function once, get a full spec for free
- Generates **`/openapi.json`** and **`/openapi.yaml`**
- Ships an embedded **Swagger UI (`/docs`)**
- Supports **query / path / header `parameters`**, **requestBody**, **responses**, `tags`
- Optional **Pydantic** integration for request / response schema inference
  *(works without Pydantic too – zero hard dependency)*

---

## Installation

```bash
pip install azure-functions-openapi
```

For local development:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .[dev]
```

---

## Quick Start

The snippet below creates a Function App with a single HTTP trigger and auto‑generated Swagger docs.

```bash
# 1) create & activate a venv
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2) install Azure Functions runtime + this package
pip install azure-functions azure-functions-worker azure-functions-openapi

# 3) scaffold a Functions project
func init hello_openapi --python
cd hello_openapi

# 4) add a new file function_app.py
```

```python
import azure.functions as func
import json
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    route="/api/http_trigger",
    summary="Say hello",
    description="""Returns a greeting.

You can pass the name:

- query string : `?name=Azure`
- JSON body    : `{ "name": "Azure" }`
""",
    parameters=[{
        "name": "name",
        "in": "query",
        "required": True,
        "schema": {"type": "string"},
        "description": "Name to greet"
    }],
    response={
        200: {
            "description": "Greeting",
            "content": {"application/json": {"examples":{
                "default":{"value":{"message":"Hello, Azure!"}}
            }}}
        },
        400: {"description": "Missing name"}
    }
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name") or (req.get_json().get("name") if req.method == "POST" else None)
    if not name:
        return func.HttpResponse("name required", status_code=400)
    return func.HttpResponse(json.dumps({"message": f"Hello, {name}!"}),
                             mimetype="application/json")

# OpenAPI endpoints
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def spec_json(req): return func.HttpResponse(get_openapi_json(), mimetype="application/json")

@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def spec_yaml(req): return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml")

@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req):   # minimal inline HTML
    return func.HttpResponse(
        '<!doctype html><html><head><link rel="stylesheet" '
        'href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"></head><body>'
        '<div id="swagger-ui"></div>'
        '<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>'
        '<script>SwaggerUIBundle({url:"/api/openapi.json",dom_id:"#swagger-ui"});</script>'
        '</body></html>', mimetype="text/html")
```

```bash
# 5) run locally
func start
```

| Endpoint | What you get |
|----------|--------------|
| `http://localhost:7071/api/http_trigger?name=Azure` | **HTTP 200** → `{"message":"Hello, Azure!"}` |
| `http://localhost:7071/api/openapi.json` | Raw OpenAPI 3 spec |
| `http://localhost:7071/api/docs` | Interactive Swagger UI |

```bash
# 6) deploy to Azure
func azure functionapp publish <FUNCTION-APP-NAME> --python
```

Swagger UI will be live at:

```
https://<FUNCTION-APP-NAME>.azurewebsites.net/api/docs
```

---

## Example with Pydantic models

```python
from pydantic import BaseModel
from azure_functions_openapi.decorator import openapi

class RequestModel(BaseModel):  name: str
class ResponseModel(BaseModel): message: str

@openapi(
    summary="Greet user (Pydantic)",
    request_model=RequestModel,
    response_model=ResponseModel,
    tags=["Example"]
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

This library targets **Pydantic v2**. v1 is **not supported**.

---

## Documentation

Full docs → <https://yeongseon.github.io/azure-functions-openapi/>

* Development workflow, tests & lint: `docs/development.md`
* Contribution guidelines: `docs/contributing.md`

---

## License

MIT © 2025 Yeongseon Choe
