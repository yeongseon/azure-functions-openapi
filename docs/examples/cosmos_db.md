# Cosmos DB Example

Demonstrates a Cosmos DB trigger with an HTTP metadata endpoint.

## Key Concepts

- Cosmos DB change feed processing
- OpenAPI endpoint for service status

## Sample

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.cosmos_db_trigger(
    arg_name="documents",
    container_name="items",
    database_name="appdb",
    connection="CosmosConnection",
)
def cosmos_change(documents: func.DocumentList) -> None:
    for doc in documents:
        _ = doc


@app.route(route="cosmos/status", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Cosmos change feed status", route="/api/cosmos/status", tags=["Cosmos"])
def cosmos_status(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("OK")
```

## Notes

- Use Cosmos DB triggers for change feed processing.
- Document operational endpoints separately with OpenAPI.
