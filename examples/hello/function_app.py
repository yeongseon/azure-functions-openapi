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
    """
    HTTP trigger function that returns a greeting message.
    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the greeting message.
    """
    logging.info("Python HTTP trigger processed a request.")

    # 1 Try query-string first
    name = req.params.get("name")

    # 2️. Fall back to JSON body
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
    """
    Get OpenAPI JSON specification.

    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI JSON specification.")
    return func.HttpResponse(get_openapi_json(), mimetype="application/json")


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get OpenAPI YAML specification.

    Parameters:
        req: The HTTP request object.
    Returns:
        A YAML response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI YAML specification.")
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml")


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    """
    Serve Swagger UI for OpenAPI documentation.

    Parameters:
        req: The HTTP request object.
    Returns:
        An HTML response containing the Swagger UI.
    """
    logging.info("Serving Swagger UI for OpenAPI documentation.")
    # Render the Swagger UI using the helper function
    return render_swagger_ui()
