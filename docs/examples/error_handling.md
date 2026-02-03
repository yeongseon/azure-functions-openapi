# Error Handling and Validation Example

Shows how to document error responses and validate input.

## Key Concepts

- Error response schemas
- Input validation

## Sample

```python
import json
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.route(route="validate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Validate input",
    route="/api/validate",
    response={
        200: {"description": "Valid input"},
        400: {"description": "Invalid input"},
    },
)
def validate(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    if "name" not in data:
        return func.HttpResponse(
            json.dumps({"error": "name is required"}),
            status_code=400,
            mimetype="application/json",
        )
    return func.HttpResponse("OK")
```

## Notes

- Describe error responses in `response` for OpenAPI.
- Return consistent JSON error payloads.
