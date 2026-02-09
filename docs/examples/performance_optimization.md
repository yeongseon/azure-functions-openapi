# Performance Optimization Example

Highlights performance optimization techniques.

## Key Concepts

- Performance optimization via efficient OpenAPI generation

## Sample

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json

app = func.FunctionApp()


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="OpenAPI JSON", route="/api/openapi.json", tags=["Docs"])
def openapi_json(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(), mimetype="application/json")
```

## Notes

- Keep OpenAPI generation lean for faster responses.
