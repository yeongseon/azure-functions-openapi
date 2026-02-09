# Timer Trigger Example

Shows a timer-triggered function alongside an HTTP endpoint.

## Key Concepts

- Timer trigger usage
- Separation of background work and documentation
- Separation of background work and documentation

## Sample

```python
import json
import azure.functions as func

from azure_functions_openapi.decorator import openapi

app = func.FunctionApp()


@app.schedule(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def refresh_docs(timer: func.TimerRequest) -> None:
    # Background job, no OpenAPI metadata required.
    pass


@app.route(route="status", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Status endpoint", route="/api/status", tags=["Docs"])
def status(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"status": "ok"}), mimetype="application/json")
```

## Notes

- Timer triggers do not expose OpenAPI docs directly.
- Provide separate HTTP endpoints for operational checks when needed.
