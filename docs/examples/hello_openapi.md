# Hello OpenAPI Example

The `hello_openapi` example demonstrates the most minimal usage of the `@openapi` decorator.

### Files

- `examples/hello_openapi/function_app.py`
- `examples/hello_openapi/host.json`
- `examples/hello_openapi/requirements.txt`

### Requirements

- Python **3.10+**
- Azure Functions Core Tools

### Key Concepts

- One route
- No request model
- Returns a simple greeting response

### Sample

```python
@app.route(route="hello", ...)
@openapi(summary="Hello", description="Returns a greeting.", response_model=HelloResponse)
def hello(req: HttpRequest) -> HttpResponse:
    ...
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
