import logging
from typing import Any, Dict, List, cast

import azure.functions as func
from pydantic import BaseModel, ValidationError

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui

# Define the Azure Function App instance
app = func.FunctionApp()


# Pydantic model for request payload
class TodoCreateRequest(BaseModel):
    title: str


# Pydantic model for update payload
class TodoUpdateRequest(BaseModel):
    id: int
    title: str
    done: bool


# Pydantic model for single todo item response
class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool


# Pydantic wrapper model for a list of todos
class TodoListResponse(BaseModel):
    todos: List[TodoResponse]


# In-memory data store
TODOS: List[Dict[str, Any]] = []


@app.route(route="create_todo", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@openapi(
    summary="Create a new todo",
    description="Add a new todo item with a title.",
    tags=["Todos"],
    operation_id="createTodo",
    route="/api/create_todo",
    method="post",
    parameters=[],
    request_model=TodoCreateRequest,
    request_body=None,
    response_model=TodoResponse,
    response={
        201: {"description": "Todo created successfully"},
        400: {"description": "Invalid request"},
    },
)
def create_todo(req: func.HttpRequest) -> func.HttpResponse:
    """
    Create a new todo item.

    Parameters:
        req: The HTTP request object containing the todo data.
    Returns:
        A JSON response with the created todo item.
    """
    logging.info("Creating a new todo")
    try:
        data = req.get_json()
        model = TodoCreateRequest(**data)
        todo = {"id": len(TODOS) + 1, "title": model.title, "done": False}
        TODOS.append(todo)

        return func.HttpResponse(
            TodoResponse(**cast(Dict[str, Any], todo)).model_dump_json(),
            status_code=201,
            mimetype="application/json",
        )
    except (ValueError, ValidationError):
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="list_todos", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@openapi(
    summary="List all todos",
    description="Retrieve the full list of todos.",
    tags=["Todos"],
    operation_id="listTodos",
    route="/api/list_todos",
    method="get",
    parameters=[],
    request_model=None,
    request_body=None,
    response_model=TodoListResponse,
    response={200: {"description": "List of todos"}},
)
def list_todos(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get all todo items.

    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the list of todos.
    """
    logging.info("Listing all todos")
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
        todos_response.model_dump_json(), mimetype="application/json", status_code=200
    )


@app.route(route="get_todo", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@openapi(
    summary="Get a todo by ID",
    description="Retrieve a specific todo by its ID.",
    tags=["Todos"],
    operation_id="getTodo",
    route="/api/get_todo",
    method="get",
    parameters=[
        {
            "name": "id",
            "in": "query",
            "required": True,
            "description": "The ID of the todo item to retrieve.",
            "schema": {"type": "integer"},
        }
    ],
    request_model=None,
    request_body=None,
    response_model=TodoResponse,
    response={
        200: {"description": "Todo item"},
        400: {"description": "Invalid request"},
        404: {"description": "Not found"},
    },
)
def get_todo(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get a specific todo item by ID.

    Parameters:
        req: The HTTP request object with query parameter `id`.
    Returns:
        A JSON response containing the todo item or 404 if not found.
    """
    logging.info("Getting a todo by ID")
    try:
        todo_id = int(req.params.get("id", ""))
        todo = next((t for t in TODOS if t["id"] == todo_id), None)
        if todo:
            return func.HttpResponse(
                TodoResponse(
                    id=cast(int, todo["id"]),
                    title=cast(str, todo["title"]),
                    done=cast(bool, todo["done"]),
                ).model_dump_json(),
                mimetype="application/json",
                status_code=200,
            )
        return func.HttpResponse("Todo not found", status_code=404)
    except Exception:
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="update_todo", auth_level=func.AuthLevel.ANONYMOUS, methods=["PUT"])
@openapi(
    summary="Update a todo",
    description="Update the title and done status of a todo.",
    tags=["Todos"],
    operation_id="updateTodo",
    route="/api/update_todo",
    method="put",
    parameters=[],
    request_model=TodoUpdateRequest,
    request_body=None,
    response_model=TodoResponse,
    response={
        200: {"description": "Todo updated"},
        400: {"description": "Invalid request"},
        404: {"description": "Not found"},
    },
)
def update_todo(req: func.HttpRequest) -> func.HttpResponse:
    """
    Update an existing todo item.

    Parameters:
        req: The HTTP request object containing the updated data.
    Returns:
        A JSON response with the updated todo item or 404 if not found.
    """
    logging.info("Updating a todo")
    try:
        model = TodoUpdateRequest(**req.get_json())
        for todo in TODOS:
            if todo["id"] == model.id:
                todo["title"] = model.title
                todo["done"] = model.done
                return func.HttpResponse(
                    TodoResponse(
                        id=cast(int, todo["id"]),
                        title=cast(str, todo["title"]),
                        done=cast(bool, todo["done"]),
                    ).model_dump_json(),
                    mimetype="application/json",
                    status_code=200,
                )
        return func.HttpResponse("Todo not found", status_code=404)
    except (ValueError, ValidationError):
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="delete_todo", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
@openapi(
    summary="Delete a todo",
    description="Delete a todo item by its ID.",
    tags=["Todos"],
    operation_id="deleteTodo",
    route="/api/delete_todo",
    method="delete",
    parameters=[
        {
            "name": "id",
            "in": "query",
            "required": True,
            "description": "The ID of the todo item to delete.",
            "schema": {"type": "integer"},
        }
    ],
    request_model=None,
    request_body=None,
    response_model=None,
    response={
        204: {"description": "Todo deleted"},
        400: {"description": "Invalid request"},
        404: {"description": "Not found"},
    },
)
def delete_todo(req: func.HttpRequest) -> func.HttpResponse:
    """
    Delete a todo item by ID.

    Parameters:
        req: The HTTP request object with query parameter `id`.
    Returns:
        A 204 response if deleted, or 404 if not found.
    """
    logging.info("Deleting a todo")
    try:
        todo_id = int(req.params.get("id", ""))
        global TODOS
        before = len(TODOS)
        TODOS = [t for t in TODOS if t["id"] != todo_id]
        after = len(TODOS)

        if before == after:
            return func.HttpResponse("Todo not found", status_code=404)
        return func.HttpResponse(status_code=204)
    except Exception:
        return func.HttpResponse("Invalid request", status_code=400)


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_spec")
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate OpenAPI specification in JSON format.

    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI spec")
    return func.HttpResponse(get_openapi_json(), mimetype="application/json", status_code=200)


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_yaml_spec")
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate OpenAPI specification in YAML format.

    Parameters:
        req: The HTTP request object.
    Returns:
        A YAML response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI YAML spec")
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml", status_code=200)


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    """
    Serve Swagger UI for OpenAPI documentation.
    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the OpenAPI specification.
    """
    logging.info("Serving Swagger UI")
    # Render the Swagger UI using the helper function
    return render_swagger_ui()
