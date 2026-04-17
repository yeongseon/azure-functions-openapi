# Todo API Example

This example demonstrates a multi-endpoint API documented with `@openapi`.

Source: `examples/todo_crud/function_app.py`

## Overview

The app implements an in-memory Todo service with:

- create, list, get, update, delete routes
- Pydantic request/response models
- OpenAPI JSON, YAML, and Swagger UI endpoints

!!! note
    Storage is in-memory (`TODOS` list). Data resets when the process restarts.

## Endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/create_todo` | Create a todo |
| `GET` | `/api/list_todos` | List all todos |
| `GET` | `/api/get_todo?id=<id>` | Get one todo |
| `PUT` | `/api/update_todo` | Update one todo |
| `DELETE` | `/api/delete_todo?id=<id>` | Delete one todo |
| `GET` | `/api/openapi.json` | OpenAPI JSON |
| `GET` | `/api/openapi.yaml` | OpenAPI YAML |
| `GET` | `/api/docs` | Swagger UI |

## Data models used

- `TodoCreateRequest`
- `TodoUpdateRequest`
- `TodoResponse`
- `TodoListResponse`

These models are used by `@openapi` to generate schemas automatically.

## How the docs are configured

Each operation has explicit metadata for:

- `summary` and `description`
- `tags=["Todos"]`
- `operation_id` (for stable client generation)
- method and route override
- request and response model mapping

Example (`create_todo`):

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
        201: {"description": "Todo created successfully"},
        400: {"description": "Invalid request"},
    },
)
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r examples/todo_crud/requirements.txt
func start
```

## Test flow with `curl`

### 1) Create todo

```bash
curl -X POST "http://localhost:7071/api/create_todo" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write docs"}'
```

Expected output:

```json
{"id":1,"title":"Write docs","done":false}
```

### 2) List todos

```bash
curl "http://localhost:7071/api/list_todos"
```

Expected output:

```json
{"todos":[{"id":1,"title":"Write docs","done":false}]}
```

### 3) Get one todo

```bash
curl "http://localhost:7071/api/get_todo?id=1"
```

Expected output:

```json
{"id":1,"title":"Write docs","done":false}
```

### 4) Update todo

```bash
curl -X PUT "http://localhost:7071/api/update_todo" \
  -H "Content-Type: application/json" \
  -d '{"id":1,"title":"Write better docs","done":true}'
```

Expected output:

```json
{"id":1,"title":"Write better docs","done":true}
```

### 5) Delete todo

```bash
curl -i -X DELETE "http://localhost:7071/api/delete_todo?id=1"
```

Expected status:

```text
HTTP/1.1 204 No Content
```

## Generated OpenAPI endpoints

Fetch JSON spec:

```bash
curl "http://localhost:7071/api/openapi.json"
```

Fetch YAML spec:

```bash
curl "http://localhost:7071/api/openapi.yaml"
```

You should see all five CRUD operations under `paths` and schemas under `components.schemas`.

## Swagger UI

Open:

`http://localhost:7071/api/docs`

Expected behavior:

- all `Todos` operations grouped under one tag
- request body editors for `POST` and `PUT`
- query parameter fields for `GET /get_todo` and `DELETE /delete_todo`

## Screenshot references

- Swagger UI with all Todo operations: `docs/assets/todo_crud_swagger_ui_preview.png`
- OpenAPI JSON snippet for Todo schemas: `docs/assets/todo_crud_openapi_spec_preview.png`

## Error cases to verify

- invalid JSON body on create/update returns `400`
- unknown ID on get/update/delete returns `404`
- missing query parameter `id` on get/delete returns `400`

## Production takeaways

- Use explicit `operation_id` values to stabilize generated SDKs
- Keep response maps (`response={...}`) complete for non-2xx outcomes
- Move from in-memory list to persistent storage without changing API docs contract shape

## Next example

See [With Validation Example](with_validation.md) for integration with `azure-functions-validation-python` so runtime validation and OpenAPI docs share the same models.
