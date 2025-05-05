from typing import Callable, Dict, Any, Optional, Type, List
from pydantic import BaseModel

# Global registry to hold OpenAPI metadata for each function
_openapi_registry: Dict[str, Dict[str, Any]] = {}


def openapi(
    summary: str = "",
    description: str = "",
    response: Optional[Dict[int, Dict[str, Any]]] = None,
    parameters: Optional[list] = None,
    request_body: Optional[Dict[str, Any]] = None,
    request_model: Optional[Type[BaseModel]] = None,
    response_model: Optional[Type[BaseModel]] = None,
    route: Optional[str] = None,
    method: Optional[str] = None,
    operation_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Callable:
    """
    Decorator to attach OpenAPI metadata to a function.

    :param summary: Short summary of the endpoint
    :param description: Detailed description
    :param response: Dictionary of response codes and descriptions
    :param parameters: List of parameters for the endpoint
    :param request_body: Schema for the request body (manual)
    :param request_model: Pydantic model for the request body (auto schema)
    :param response_model: Pydantic model for the response body (auto schema)
    :param route: Optional override for route path
    :param method: Optional override for HTTP method
    :param operation_id: Unique operation identifier (optional)
    :param tags: List of tags to group the operation (optional)
    :return: Decorated function with metadata registered
    """

    def decorator(func: Callable) -> Callable:
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
    Retrieve the current OpenAPI metadata registry.

    :return: Dictionary containing metadata for all registered functions
    """
    return _openapi_registry
