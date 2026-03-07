# Azure Functions OpenAPI

`azure-functions-openapi` adds OpenAPI (Swagger) documentation to the **Azure Functions Python v2 programming model**.
It is built for decorator-based `func.FunctionApp()` applications and HTTP-triggered functions.

## Highlights

- `@openapi` decorator for endpoint metadata
- Generated `/openapi.json`, `/openapi.yaml`, and `/docs`
- Optional Pydantic v1 and v2 schema support
- Swagger UI helper with secure defaults
- CLI tooling for generation and validation workflows

## Example

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi


app = func.FunctionApp()


@app.function_name(name="hello")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@openapi(summary="Hello endpoint", route="/api/hello", tags=["Example"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("ok")
```

See the Installation and Usage guides for the full setup, including the OpenAPI JSON, YAML, and Swagger UI routes.

## Examples

- Representative: `examples/hello_openapi`
- Complex: `examples/todo_crud_api`
