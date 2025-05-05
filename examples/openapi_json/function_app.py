import azure.functions as func
import logging
from pydantic import BaseModel, ValidationError
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml

app = func.FunctionApp()


# Request and Response models using Pydantic
class RequestModel(BaseModel):
    name: str


class ResponseModel(BaseModel):
    message: str


@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="HTTP Trigger with name parameter",
    description=""""
Returns a greeting using the name from query or body.

### Usage
You can pass the name:
- via query string: `?name=Azure`
- or via JSON body:

```json
{ "name": "Azure" }
```
""",
    request_model=RequestModel,
    response_model=ResponseModel,
    operation_id="greetUser",
    tags=["Example"],
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
        }
    },
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            data = req.get_json()
            model = RequestModel(**data)
            name = model.name
        except (ValueError, ValidationError):
            return func.HttpResponse("Invalid request", status_code=400)

    message = f"Hello, {name}!" if name else "Hello!"
    return func.HttpResponse(
        ResponseModel(message=message).model_dump_json(),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_openapi_json(), mimetype="application/json", status_code=200
    )


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_openapi_yaml(),
        mimetype="application/x-yaml",
        status_code=200,
    )


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Swagger UI</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        SwaggerUIBundle({
          url: "/openapi.json",
          dom_id: '#swagger-ui'
        });
      </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
