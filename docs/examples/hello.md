# Hello OpenAPI Example

This example is the smallest complete Azure Functions app that demonstrates:

- one documented endpoint
- generated OpenAPI JSON and YAML
- Swagger UI route

Source: `examples/hello/function_app.py`

## What this example includes

- `GET /api/http_trigger` with query parameter `name`
- `GET /api/openapi.json`
- `GET /api/openapi.yaml`
- `GET /api/docs`

## Complete code

```python
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

### Usage

You can pass the name:

- via query string: `?name=Azure`
- via JSON body:

  ```json
  { "name": "Azure" }
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
    logging.info("Python HTTP trigger processed a request.")

    name = req.params.get("name")

    if not name:
        try:
            body = req.get_json()
        except ValueError:
            body = {}

        if isinstance(body, dict):
            name = body.get("name")

    if not name:
        return func.HttpResponse("Invalid request – `name` is required", status_code=400)

    message = f"Hello, {name}!"
    return func.HttpResponse(
        json.dumps({"message": message}),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Generating OpenAPI JSON specification.")
    return func.HttpResponse(get_openapi_json(), mimetype="application/json")


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Generating OpenAPI YAML specification.")
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml")


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Serving Swagger UI for OpenAPI documentation.")
    return render_swagger_ui()
```

## Step-by-step run

1. Create and activate virtual environment
2. Install dependencies from `examples/hello/requirements.txt`
3. Start local runtime with `func start`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r examples/hello/requirements.txt
func start
```

## Test the endpoint

### Success case

```bash
curl "http://localhost:7071/api/http_trigger?name=Azure"
```

Expected output:

```json
{"message":"Hello, Azure!"}
```

### Error case

```bash
curl "http://localhost:7071/api/http_trigger"
```

Expected output:

```text
Invalid request – `name` is required
```

## Inspect generated spec

JSON:

```bash
curl "http://localhost:7071/api/openapi.json"
```

YAML:

```bash
curl "http://localhost:7071/api/openapi.yaml"
```

You should see one path for `/api/http_trigger` with:

- `operationId: greetUser`
- tag `Example`
- query parameter `name`
- `200` and `400` responses

## Open Swagger UI

Open `http://localhost:7071/api/docs` in your browser.

Expected behavior:

- the `http_trigger` operation appears immediately
- parameter input for `name` is available
- `Try it out` sends request to your local function app

## Screenshot references

- OpenAPI JSON preview: `docs/assets/hello_openapi_spec_preview.png`
- Swagger UI preview: `docs/assets/hello_openapi_swagger_ui_preview.png`

## Why this example matters

This sample proves the smallest production pattern:

- document handlers in-place with decorators
- generate machine-readable contract from runtime metadata
- expose human-friendly interactive docs in the same service

## Next example

Move to [Todo API Example](todo_crud.md) to see multiple endpoints, request/response models, and CRUD-style flows.
