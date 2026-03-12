# Usage Guide: azure-functions-openapi

This guide documents **Azure Functions Python v2** applications using `azure-functions-openapi`.
Examples below assume a decorator-based `func.FunctionApp()` application.

## `@openapi` Decorator

Use the `@openapi` decorator to attach OpenAPI metadata to each HTTP function.
This metadata is used at runtime to generate:

- `/openapi.json`
- `/openapi.yaml`
- `/docs`

```python
@openapi(
    summary="Create a new todo",
    description="Add a new todo item with a title.",
    tags=["Todos"],
    operation_id="createTodo",
    route="/api/create_todo",
    method="post",
    request_model=TodoCreateRequest,
    response_model=TodoResponse,
    response={
        201: {"description": "Todo created"},
        400: {"description": "Invalid request"},
    },
)
```

## Pydantic Models

Request and response models may use **Pydantic v1 or v2**.

```python
class TodoCreateRequest(BaseModel):
    title: str


class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool
```

**Note:** `request_model` and `response_model` require Pydantic `BaseModel` classes. To use raw dict schemas instead, use `request_body` and `response` parameters respectively.


## Routing

Pair `@openapi` with Azure Functions v2 route decorators:

```python
@app.function_name(name="create_todo")
@app.route(route="create_todo", methods=["POST"])
@openapi(route="/api/create_todo", method="post", summary="Create todo")
def create_todo(req: func.HttpRequest) -> func.HttpResponse:
    _ = req
    return func.HttpResponse("Created", status_code=201)
```

## Exposing Documentation Endpoints

Add the OpenAPI and Swagger UI endpoints to your v2 `FunctionApp`:

```python
@app.function_name(name="openapi_spec")
@app.route(route="openapi.json", methods=["GET"])
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_json(
        title="Todo API",
        description="OpenAPI document for the Todo API.",
    )


@app.function_name(name="openapi_yaml_spec")
@app.route(route="openapi.yaml", methods=["GET"])
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_yaml(
        title="Todo API",
        description="OpenAPI document for the Todo API.",
    )


@app.function_name(name="swagger_ui")
@app.route(route="docs", methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

## Security Schemes

Use the `security` and `security_scheme` parameters on `@openapi` to declare
operation-level security requirements and register the corresponding
`components.securitySchemes` entry in the generated spec.

### Per-Decorator (Distributed)

Attach the scheme definition directly alongside the security requirement:

```python
@openapi(
    summary="List items",
    route="/api/items",
    method="get",
    security=[{"BearerAuth": []}],
    security_scheme={
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
)
```

### Central (Explicit)

Pass `security_schemes` to the spec-generation functions when you prefer a
single source of truth:

```python
SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}

@app.function_name(name="openapi_spec")
@app.route(route="openapi.json", methods=["GET"])
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_json(
        title="My API",
        security_schemes=SCHEMES,
    )
```

Both approaches can be combined — per-decorator and central schemes are
merged automatically. If the same scheme name appears in both, the central
definition takes precedence.

### Supported Scheme Types

| `type` value | Description |
| --- | --- |
| `apiKey` | API key (header, query, or cookie) |
| `http` | HTTP authentication (Bearer, Basic, etc.) |
| `oauth2` | OAuth 2.0 flows |
| `openIdConnect` | OpenID Connect Discovery |

## Output Routes

| Route | Format | Description |
| --- | --- | --- |
| `/openapi.json` | JSON | Full OpenAPI schema |
| `/openapi.yaml` | YAML | YAML version of the schema |
| `/docs` | Swagger UI | Interactive documentation UI |

## Notes

- This package is for the Azure Functions Python **v2** programming model.
- It does not support the legacy `function.json`-based v1 model.
- Pydantic v1 and v2 support refers to schema generation only, not Azure Functions programming model support.
- `get_openapi_json()` and `get_openapi_yaml()` accept an optional `description` argument for the top-level OpenAPI `info.description` field.
