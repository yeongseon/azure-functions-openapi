# Todo API Example

The `todo_crud_api` example shows how to build a basic Todo API using:

- Azure Functions (v2 model)
- `@openapi` decorators
- Pydantic models

### Features

- `POST /create_todo` to add a new item
- `GET /list_todos` to fetch all items

### Directory

- `examples/todo_crud_api/function_app.py`
- `examples/todo_crud_api/host.json`

### Requirements

- Python **3.10+**
- Azure Functions Core Tools

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

- `POST /api/create_todo`
- `GET /api/list_todos`
- `GET /api/get_todo`
- `PUT /api/update_todo`
- `DELETE /api/delete_todo`
- `GET /api/openapi.json`
- `GET /api/openapi.yaml`
- `GET /api/docs`
