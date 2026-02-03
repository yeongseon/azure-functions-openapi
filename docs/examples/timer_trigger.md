# Timer Trigger Example

Shows a timer-triggered function alongside an HTTP endpoint for metrics.

## Key Concepts

- Timer trigger usage
- Monitoring data surfaced via HTTP
- Separation of background work and documentation

## Sample

```python
import json
import azure.functions as func

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.monitoring import get_performance_monitor

app = func.FunctionApp()


@app.schedule(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def refresh_cache(timer: func.TimerRequest) -> None:
    # Background job, no OpenAPI metadata required.
    pass


@app.route(route="metrics", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Performance metrics", route="/api/metrics", tags=["Monitoring"])
def metrics(req: func.HttpRequest) -> func.HttpResponse:
    monitor = get_performance_monitor()
    return func.HttpResponse(
        json.dumps(monitor.get_response_time_stats()),
        mimetype="application/json",
    )
```

## Notes

- Timer triggers do not expose OpenAPI docs directly.
- Provide separate HTTP endpoints for monitoring when needed.
