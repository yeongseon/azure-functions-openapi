from typing import Callable, Dict, Any, Optional, Type, List, TypeVar
from pydantic import BaseModel

# Define a generic type variable for functions
F = TypeVar("F", bound=Callable[..., Any])

# Global registry to hold OpenAPI metadata for each function
_openapi_registry: Dict[str, Dict[str, Any]] = {}


def openapi(
    summary: str = "",
    description: str = "",
    response: Optional[Dict[int, Dict[str, Any]]] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    request_model: Optional[Type[BaseModel]] = None,
    response_model: Optional[Type[BaseModel]] = None,
    route: Optional[str] = None,
    method: Optional[str] = None,
    operation_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Callable[[F], F]:
    """
    Decorator to attach OpenAPI metadata to a function.

    Example usage:

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
            tags=["Example"]
        )
        def my_func(req: func.HttpRequest) -> func.HttpResponse:
            ...

    Parameters:
        summary: Short summary of the endpoint.
        description: Detailed description (Markdown supported).
        response: Manual response schema (dictionary of status codes).
        parameters: List of parameters (query/path/header).
        request_body: Manual requestBody schema.
        request_model: Pydantic model for request body.
        response_model: Pydantic model for response body.
        route: Optional override for HTTP route path.
        method: Optional override for HTTP method.
        operation_id: Custom OpenAPI operationId.
        tags: List of tags to group the endpoint.

    Returns:
        Callable function with metadata registered.
    """

    def decorator(func: F) -> F:
        _openapi_registry[func.__name__] = {
            "summary": summary,
            "description": description,
            "response": response or {},
            "parameters": parameters or [],
            "request_body": request_body,
            "request_model": request_model,
            "response_model": response_model,
            "route": route,
            "method": method,
            "operation_id": operation_id,
            "tags": tags or ["default"],
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
