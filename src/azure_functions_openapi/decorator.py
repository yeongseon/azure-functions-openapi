# src/azure_functions_openapi/decorator.py
from typing import Callable, Dict, Any, Optional

# Global registry to hold OpenAPI metadata for each function
_openapi_registry: Dict[str, Dict[str, Any]] = {}


def openapi(
    summary: str = "",
    description: str = "",
    response: Optional[Dict[int, Dict[str, Any]]] = None,
    parameters: Optional[list] = None,
    request_body: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to attach OpenAPI metadata to a function.

    :param summary: Short summary of the endpoint
    :param description: Detailed description
    :param response: Dictionary of response codes and descriptions
    :param parameters: List of parameters for the endpoint
    :param request_body: Dictionary describing the request body
    :return: Decorated function with metadata registered
    """

    def decorator(func: Callable) -> Callable:
        _openapi_registry[func.__name__] = {
            "summary": summary,
            "description": description,
            "response": response or {},
            "parameters": parameters or [],
            "request_body": request_body or {},
        }
        return func

    return decorator


def get_openapi_registry() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve the current OpenAPI metadata registry.

    :return: Dictionary containing metadata for all registered functions
    """
    return _openapi_registry
