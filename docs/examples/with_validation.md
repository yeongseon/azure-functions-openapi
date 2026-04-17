# With Validation Example

This example shows how to combine:

- `azure-functions-openapi-python` for OpenAPI documentation
- `azure-functions-validation-python` for runtime request/response validation

Source: `examples/with_validation/function_app.py`

## Why this pattern is useful

You define one Pydantic model and reuse it in both decorators:

- `@openapi(...)` -> docs/spec generation
- `@validate_http(...)` -> runtime parsing and validation

That keeps contract and validation logic synchronized.

## Endpoints

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/api/users` | Create user from validated JSON body |
| `GET` | `/api/users/{user_id}` | Get user with validated query params |
| `GET` | `/api/openapi.json` | OpenAPI JSON |
| `GET` | `/api/openapi.yaml` | OpenAPI YAML |
| `GET` | `/api/docs` | Swagger UI |

## Core models

```python
class CreateUserRequest(BaseModel):
    name: str
    email: str


class UserQuery(BaseModel):
    include_profile: bool = Field(default=False)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

## Decorator pairing example

```python
@app.function_name(name="create_user")
@app.route(route="users", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Create a new user",
    description="Create a user with name and email.",
    tags=["Users"],
    operation_id="createUser",
    route="/api/users",
    method="post",
    request_model=CreateUserRequest,
    response_model=UserResponse,
    response={201: {"description": "User created"}, 422: {"description": "Validation error"}},
)
@validate_http(body=CreateUserRequest, response_model=UserResponse)
def create_user(req: func.HttpRequest, body: CreateUserRequest) -> UserResponse:
    ...
```

## Complete behavior summary

### `POST /api/users`

- body is validated against `CreateUserRequest`
- valid request returns `UserResponse`
- invalid request shape triggers validation error path

### `GET /api/users/{user_id}`

- route param `user_id` is read from `req.route_params`
- query is validated via `UserQuery`
- returns `404` when user does not exist

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r examples/with_validation/requirements.txt
func start
```

## Test with `curl`

### 1) Create user (valid)

```bash
curl -X POST "http://localhost:7071/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ava","email":"ava@example.com"}'
```

Expected output:

```json
{"id":1,"name":"Ava","email":"ava@example.com"}
```

### 2) Create user (invalid body)

```bash
curl -X POST "http://localhost:7071/api/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ava"}'
```

Expected behavior:

- request fails validation
- response status and payload come from `azure-functions-validation-python`

### 3) Get user (valid)

```bash
curl "http://localhost:7071/api/users/1?include_profile=true"
```

Expected output:

```json
{"id":1,"name":"Ava","email":"ava@example.com"}
```

### 4) Get unknown user

```bash
curl -i "http://localhost:7071/api/users/999"
```

Expected status:

```text
HTTP/1.1 404 Not Found
```

## Inspect generated docs

OpenAPI JSON:

```bash
curl "http://localhost:7071/api/openapi.json"
```

Swagger UI:

`http://localhost:7071/api/docs`

In Swagger UI, confirm:

- `Users` tag groups both operations
- `CreateUserRequest` appears as request schema
- `UserResponse` appears as response schema
- `user_id` path parameter and `include_profile` query parameter are documented

## Screenshot references

- Users endpoints in Swagger UI: `docs/assets/with_validation_swagger_ui_preview.png`
- Generated schema components: `docs/assets/with_validation_openapi_spec_preview.png`

## Notes on status codes

`@openapi(response={...})` documents expected outcomes. Runtime status behavior is still controlled by your function code and validation decorator behavior.

## Production guidance

- Reuse the same Pydantic models in both decorators to prevent schema drift
- Keep `operation_id` stable for client generation
- Add explicit `422`/`400` error docs for validation failures
- Combine with auth docs (`security`, `security_scheme`) where needed

## Related docs

- [Usage](../usage.md)
- [Configuration](../configuration.md)
- [FAQ](../faq.md)
- [Troubleshooting](../troubleshooting.md)
