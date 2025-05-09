# src/azure_functions_openapi/decorator.py
from typing import Callable, Dict, Any, Optional, Type, List, TypeVar
from pydantic import BaseModel

# Define a generic type variable for functions
F = TypeVar("F", bound=Callable[..., Any])

# Global registry to hold OpenAPI metadata for each function
_openapi_registry: Dict[str, Dict[str, Any]] = {}


def openapi(
    # ── basic metadata ───────────────────────────────────────────
    summary: str = "",
    description: str = "",
    tags: Optional[List[str]] = None,
    operation_id: Optional[str] = None,
    # ── routing information ─────────────────────────────────────
    route: Optional[str] = None,
    method: Optional[str] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    # ── request / response schema ───────────────────────────────
    request_model: Optional[Type[BaseModel]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    response_model: Optional[Type[BaseModel]] = None,
    response: Optional[Dict[int, Dict[str, Any]]] = None,
) -> Callable[[F], F]:
    """
    Decorator that attaches OpenAPI metadata to an Azure Functions handler.

    Examples
    --------
    ### 1 · Minimal “Hello World”

    ```python
    @app.route(route="hello")
    @openapi(summary="Hello", description="Returns plain text.")
    def hello(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse("Hello, world!", status_code=200)
    ```

    ### 2 · Pydantic-powered JSON API

    ```python
    from pydantic import BaseModel

    class TodoRequest(BaseModel):
        title: str
        done: bool = False

    class TodoResponse(BaseModel):
        id: int
        title: str
        done: bool

    @app.route(route="todos/{id}", method="put")
    @openapi(
        summary="Update a todo item",
        description=\"""Update a todo and return the updated document.\""",
        tags=["Todo"],
        parameters=[{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
        request_model=TodoRequest,
        response_model=TodoResponse,
        operation_id="updateTodo",
    )
    def update_todo(req: func.HttpRequest) -> func.HttpResponse:
        # ... business logic ...
        body = TodoRequest.model_validate_json(req.get_body())
        todo = TodoResponse(id=1, **body.model_dump())
        return func.HttpResponse(
            todo.model_dump_json(),
            status_code=200,
            mimetype="application/json",
        )
    ```

    After starting the Function App you get:

    * **Swagger UI** → `http://localhost:7071/api/docs`
    * **Raw JSON spec** → `http://localhost:7071/api/openapi.json`

    Parameters
    ----------
    summary:
        Short description shown in Swagger UI.
    description:
        Longer Markdown-enabled description.
    tags:
        List of group tags.
    operation_id:
        Custom operationId (defaults to function name).
    route:
        Override for the HTTP route path (e.g. "/items/{id}").
    method:
        Explicit HTTP method if not inferrable.
    parameters:
        List of param objects (query/path/header/cookie).
    request_model:
        Pydantic model used to derive requestBody schema.
    request_body:
        Raw requestBody schema (if you don’t use Pydantic).
    response_model:
        Pydantic model used to derive 200-response schema.
    response:
        Manual responses dict keyed by status code.

    Returns
    -------
    Callable
        The original function, with its name stored in `_openapi_registry`.
    """

    def decorator(func: F) -> F:
        _openapi_registry[func.__name__] = {
            # ── basic metadata ────────────────────────────────
            "summary": summary,
            "description": description,
            "tags": tags or ["default"],
            "operation_id": operation_id,
            # ── routing info ─────────────────────────────────
            "route": route,
            "method": method,
            "parameters": parameters or [],
            # ── request / response schema ────────────────────
            "request_model": request_model,
            "request_body": request_body,
            "response_model": response_model,
            "response": response or {},
        }
        return func

    return decorator


def get_openapi_registry() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve OpenAPI metadata for all registered functions.

    Returns:
        A dictionary where each key is a function name and value is its OpenAPI metadata.
    """
    return _openapi_registry
