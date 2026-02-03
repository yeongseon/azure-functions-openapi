# Blob Storage Example

Shows a blob-triggered function with a documentation endpoint.

## Key Concepts

- Blob trigger usage
- OpenAPI endpoint for operational visibility

## Sample

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.blob_trigger(
    arg_name="blob",
    path="uploads/{name}",
    connection="BlobConnection",
)
def handle_blob(blob: func.InputStream) -> None:
    # Process blob contents
    _ = blob.read()


@app.route(route="blob/health", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Blob processing health", route="/api/blob/health", tags=["Blob"])
def blob_health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("OK")
```

## Notes

- Keep blob processing logic isolated from HTTP concerns.
- Provide a separate endpoint for monitoring and documentation.
