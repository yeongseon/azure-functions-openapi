# Hello OpenAPI Example

The `hello` example demonstrates the most minimal usage of the `@openapi` decorator.

### Files

- `examples/hello/function_app.py`
- `examples/hello/host.json`
- `examples/hello/requirements.txt`

### Requirements

- Python **3.10+**
- Azure Functions Core Tools

### Key Concepts

- One route
- No request model
- Returns a simple greeting response

### Sample

```python
@app.route(route="hello", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@openapi(summary="Hello", description="Returns a greeting.", response_model=HelloResponse)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    _ = req
    return func.HttpResponse("Hello from Azure Functions", status_code=200)
```

### Local Setup

Create a `local.settings.json` (not committed) to configure the Python worker runtime:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

Install dependencies:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally:

```bash
func start
```

### Endpoints

- `GET /api/http_trigger?name=Azure`
- `GET /api/openapi.json`
- `GET /api/openapi.yaml`
- `GET /api/docs`
