# With Validation Example

The `with_validation` example demonstrates how to use `@openapi` and `@validate_http` together, sharing the same Pydantic models for both documentation and runtime validation.

### Key Concept

Both decorators receive the **same** Pydantic model class. `@openapi` uses it to generate the OpenAPI schema, while `@validate_http` uses it to parse and validate the request at runtime.

```python
@openapi(
    summary="Create user",
    description="Create a user with request validation.",
    route="/api/users",
    method="post",
    request_model=CreateUserRequest,
    response_model=UserResponse,
)
@validate_http(body=CreateUserRequest, response_model=UserResponse)
def create_user(req: func.HttpRequest, body: CreateUserRequest) -> func.HttpResponse:
    _ = (req, body)
    return func.HttpResponse("User created", status_code=201)
```

### Files

- `examples/with_validation/function_app.py`
- `examples/with_validation/host.json`
- `examples/with_validation/requirements.txt`

### Requirements

- Python **3.10+**
- Azure Functions Core Tools
- `azure-functions-openapi`
- `azure-functions-validation`

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

- `POST /api/users`
- `GET /api/users/{user_id}`
- `GET /api/openapi.json`
- `GET /api/openapi.yaml`
- `GET /api/docs`
