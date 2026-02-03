# Queue Storage Example

Illustrates a queue-triggered function and a companion HTTP endpoint for docs.

## Key Concepts

- Queue trigger processing
- HTTP endpoint for OpenAPI documentation

## Sample

```python
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.queue_trigger(arg_name="msg", queue_name="tasks", connection="QueueConnection")
def process_queue(msg: func.QueueMessage) -> None:
    payload = msg.get_body().decode()
    # Process payload


@app.route(route="queue/status", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Queue status", route="/api/queue/status", tags=["Queue"])
def queue_status(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("OK")
```

## Notes

- Use a separate HTTP route to expose metadata and health checks.
- Keep queue trigger logic focused on background processing.
