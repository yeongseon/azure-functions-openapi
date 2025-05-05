import azure.functions as func
import logging
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json

app = func.FunctionApp()


@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="HTTP Trigger with name parameter",
    description="Returns a greeting using the name from query or body.",
    response={
        200: {
            "description": "Successful response with greeting",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "example": {"message": "Hello, John!"},
                    },
                    "examples": {
                        "sample": {
                            "summary": "Example greeting",
                            "value": {"message": "Hello, Azure!"},
                        }
                    },
                }
            },
        }
    },
    parameters=[
        {
            "name": "name",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Name to greet",
        }
    ],
    request_body={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
        "required": ["name"],
    },
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        else:
            name = req_body.get("name") if req_body else None

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200,
        )


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_openapi_json(), mimetype="application/json", status_code=200
    )


@app.route(route="swagger", auth_level=func.AuthLevel.ANONYMOUS)
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Swagger UI</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        SwaggerUIBundle({
          url: "/openapi.json",
          dom_id: '#swagger-ui',
        });
      </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
