# Authentication and Authorization Example

Demonstrates function-level authentication and documented security parameters.

## Key Concepts

- Azure Functions auth levels
- Documenting required headers

## Sample

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.route(route="secure", auth_level=func.AuthLevel.FUNCTION)
@openapi(
    summary="Secure endpoint",
    route="/api/secure",
    tags=["Security"],
    parameters=[
        {
            "name": "x-functions-key",
            "in": "header",
            "required": True,
            "schema": {"type": "string"},
            "description": "Function key for authentication",
        }
    ],
)
def secure(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("OK")
```

## Notes

- Use `AuthLevel.FUNCTION` or higher for secured endpoints.
- Document required headers so clients can authenticate.
