import azure.functions as func
import logging
from pydantic import BaseModel, ValidationError
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from typing import List, cast

# Define the Azure Function App instance
app = func.FunctionApp()


# Pydantic model for request payload
class TodoCreateRequest(BaseModel):
    title: str


# Pydantic model for single todo item response
class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool


# Pydantic wrapper model for a list of todos
class TodoListResponse(BaseModel):
    todos: List[TodoResponse]


# In-memory data store
TODOS: List[dict[str, object]] = []


@app.route(route="create_todo", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@openapi(
    summary="Create a new todo",
    description="Add a new todo item with a title.",
    request_model=TodoCreateRequest,
    response_model=TodoResponse,
    operation_id="createTodo",
    tags=["Todos"],
    response={201: {"description": "Todo created successfully"}},
)  # type: ignore[misc]
def create_todo(req: func.HttpRequest) -> func.HttpResponse:
    """
    Create a new todo item.
    """
    logging.info("Creating a new todo")
    try:
        data = req.get_json()
        model = TodoCreateRequest(**data)
        todo = {"id": len(TODOS) + 1, "title": model.title, "done": False}
        TODOS.append(todo)

        return func.HttpResponse(
            TodoResponse(
                id=cast(int, todo["id"]),
                title=cast(str, todo["title"]),
                done=cast(bool, todo["done"]),
            ).model_dump_json(),
            status_code=201,
            mimetype="application/json",
        )
    except (ValueError, ValidationError):
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="list_todos", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@openapi(
    summary="List all todos",
    description="Retrieve the full list of todos.",
    response_model=TodoListResponse,
    operation_id="listTodos",
    tags=["Todos"],
    response={200: {"description": "List of todos"}},
)  # type: ignore[misc]
def list_todos(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get all todo items.
    """
    todos_response = TodoListResponse(
        todos=[
            TodoResponse(
                id=cast(int, t["id"]),
                title=cast(str, t["title"]),
                done=cast(bool, t["done"]),
            )
            for t in TODOS
        ]
    )
    return func.HttpResponse(
        todos_response.model_dump_json(), mimetype="application/json"
    )


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_spec")
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_openapi_json(), mimetype="application/json", status_code=200
    )


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_yaml_spec")
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        get_openapi_yaml(), mimetype="application/x-yaml", status_code=200
    )


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Swagger UI</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        SwaggerUIBundle({
          url: window.location.origin + "/api/openapi.json",
          dom_id: '#swagger-ui'
        });
      </script>
    </body>
    </html>
    """
    return func.HttpResponse(html, mimetype="text/html")
