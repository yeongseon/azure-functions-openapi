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

    Example
    -------
        from pydantic import BaseModel
        from azure_functions_openapi.decorator import openapi

        class GreetingRequest(BaseModel):
            name: str

        class GreetingResponse(BaseModel):
            message: str

        @openapi(
            summary="Greet user",
            description="Returns a greeting using the name.",
            request_model=GreetingRequest,
            response_model=GreetingResponse,
            tags=["Example"],
        )
        def my_func(req: func.HttpRequest) -> func.HttpResponse:
            ...

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
