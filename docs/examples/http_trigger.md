# HTTP Trigger Example

Demonstrates a basic HTTP-triggered Azure Function with OpenAPI metadata.

## Key Concepts

- `@openapi` decorator usage
- Request and response models
- JSON response format

## Sample

```python
import json
import azure.functions as func
from pydantic import BaseModel

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


class HelloRequest(BaseModel):
    name: str


class HelloResponse(BaseModel):
    message: str


@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@openapi(
    summary="Hello",
    route="/api/hello",
    request_model=HelloRequest,
    response_model=HelloResponse,
    tags=["Example"],
)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    name = data.get("name", "world")
    return func.HttpResponse(
        json.dumps({"message": f"Hello, {name}!"}),
        mimetype="application/json",
    )
```

## Notes

- `route` in the decorator should match the HTTP trigger route.
- Use `request_model` and `response_model` for schema generation.
