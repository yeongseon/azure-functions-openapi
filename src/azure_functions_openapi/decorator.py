# src/azure_functions_openapi/decorator.py
from __future__ import annotations

import logging
import threading
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from azure_functions_openapi.errors import OpenAPIError, ValidationError
from azure_functions_openapi.utils import sanitize_operation_id, validate_route_path

# Define a generic type variable for functions
F = TypeVar("F", bound=Callable[..., Any])

# Global registry to hold OpenAPI metadata for each function
_openapi_registry: dict[str, dict[str, Any]] = {}
_registry_lock = threading.RLock()

logger = logging.getLogger(__name__)


def openapi(
    # ── basic metadata ───────────────────────────────────────────
    summary: str = "",
    description: str = "",
    tags: list[str] | None = None,
    operation_id: str | None = None,
    # ── routing information ─────────────────────────────────────
    route: str | None = None,
    method: str | None = None,
    parameters: list[dict[str, Any]] | None = None,
    security: list[dict[str, list[str]]] | None = None,
    # ── request / response schema ───────────────────────────────
    request_model: type[BaseModel] | None = None,
    request_body: dict[str, Any] | None = None,
    response_model: type[BaseModel] | None = None,
    response: dict[int, dict[str, Any]] | None = None,
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
    security:
        List of OpenAPI Security Requirement Objects.
        Example: [{"BearerAuth": []}]
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
        try:
            # Enhanced input validation and sanitization
            validated_route = _validate_and_sanitize_route(route, func.__name__)
            sanitized_operation_id = _validate_and_sanitize_operation_id(
                operation_id, func.__name__
            )
            validated_parameters = _validate_parameters(parameters, func.__name__)
            validated_security = _validate_security(security, func.__name__)
            validated_tags = _validate_tags(tags, func.__name__)

            # Validate request/response models
            _validate_models(request_model, response_model, func.__name__)

            function_id = f"{func.__module__}.{func.__qualname__}"

            with _registry_lock:
                registry_key = func.__name__
                existing = _openapi_registry.get(registry_key)
                if existing and existing.get("_function_id") != function_id:
                    existing_id = existing.get("_function_id")
                    if isinstance(existing_id, str) and existing_id not in _openapi_registry:
                        _openapi_registry[existing_id] = existing

                _openapi_registry[registry_key] = {
                    # ── basic metadata ────────────────────────────────
                    "summary": summary,
                    "description": description,
                    "tags": validated_tags,
                    "operation_id": sanitized_operation_id,
                    # ── routing info ─────────────────────────────────
                    "route": validated_route,
                    "method": method,
                    "parameters": validated_parameters,
                    "security": validated_security,
                    # ── request / response schema ────────────────────
                    "request_model": request_model,
                    "request_body": request_body,
                    "response_model": response_model,
                    "response": response or {},
                    "function_name": func.__name__,
                    "_function_id": function_id,
                }

            logger.debug(f"Registered OpenAPI metadata for function '{func.__name__}'")
            return func

        except Exception as e:
            logger.error(
                f"Failed to register OpenAPI metadata for function '{func.__name__}': {str(e)}"
            )
            raise OpenAPIError(
                message=f"Failed to register OpenAPI metadata for function '{func.__name__}'",
                details={"function_name": func.__name__, "error": str(e)},
                cause=e,
            )

    return decorator


def get_openapi_registry() -> dict[str, dict[str, Any]]:
    """
    Retrieve OpenAPI metadata for all registered functions.

    Returns:
        A dictionary where each key is a function name and value is its OpenAPI metadata.
    """
    with _registry_lock:
        return {key: value.copy() for key, value in _openapi_registry.items()}


def _validate_and_sanitize_route(route: str | None, func_name: str) -> str | None:
    """Validate and sanitize route path."""
    if not route:
        return None

    if not validate_route_path(route):
        logger.warning(
            "Invalid route path '%s' for function '%s'. Using function name as fallback.",
            route,
            func_name,
        )
        raise ValidationError(
            message=f"Invalid route path: {route}",
            details={"route": route, "function_name": func_name},
        )

    return route


def _validate_and_sanitize_operation_id(operation_id: str | None, func_name: str) -> str | None:
    """Validate and sanitize operation ID."""
    if not operation_id:
        return None

    sanitized = sanitize_operation_id(operation_id)
    if not sanitized:
        logger.warning(
            "Invalid operation ID '%s' for function '%s'. Using function name as fallback.",
            operation_id,
            func_name,
        )
        raise ValidationError(
            message=f"Invalid operation ID: {operation_id}",
            details={"operation_id": operation_id, "function_name": func_name},
        )

    return sanitized


def _validate_parameters(
    parameters: list[dict[str, Any]] | None, func_name: str
) -> list[dict[str, Any]]:
    """Validate parameters list."""
    if not parameters:
        return []

    if not isinstance(parameters, list):
        raise ValidationError(
            message="Parameters must be a list",
            details={"parameters": str(parameters), "function_name": func_name},
        )

    validated_params = []
    for i, param in enumerate(parameters):
        if not isinstance(param, dict):
            raise ValidationError(
                message=f"Parameter at index {i} must be a dictionary",
                details={"parameter_index": i, "function_name": func_name},
            )

        # Validate required fields
        required_fields = ["name", "in"]
        for field in required_fields:
            if field not in param:
                raise ValidationError(
                    message=f"Parameter at index {i} missing required field: {field}",
                    details={
                        "parameter_index": i,
                        "missing_field": field,
                        "function_name": func_name,
                    },
                )

        validated_params.append(param)

    return validated_params


def _validate_security(
    security: list[dict[str, list[str]]] | None, func_name: str
) -> list[dict[str, list[str]]]:
    """Validate OpenAPI security requirements list."""
    if not security:
        return []

    if not isinstance(security, list):
        raise ValidationError(
            message="Security must be a list",
            details={"security": str(security), "function_name": func_name},
        )

    validated_security: list[dict[str, list[str]]] = []
    for i, requirement in enumerate(security):
        if not isinstance(requirement, dict):
            raise ValidationError(
                message=f"Security requirement at index {i} must be a dictionary",
                details={"security_index": i, "function_name": func_name},
            )

        validated_requirement: dict[str, list[str]] = {}
        for scheme_name, scopes in requirement.items():
            if not isinstance(scheme_name, str) or not scheme_name.strip():
                raise ValidationError(
                    message=f"Security scheme name at index {i} must be a non-empty string",
                    details={"security_index": i, "function_name": func_name},
                )

            if not isinstance(scopes, list) or not all(isinstance(scope, str) for scope in scopes):
                raise ValidationError(
                    message=(
                        f"Security scopes for '{scheme_name}' at index {i} "
                        "must be a list of strings"
                    ),
                    details={"security_index": i, "function_name": func_name},
                )

            validated_requirement[scheme_name] = scopes

        validated_security.append(validated_requirement)

    return validated_security


def _validate_tags(tags: list[str] | None, func_name: str) -> list[str]:
    """Validate tags list."""
    if not tags:
        return ["default"]

    if not isinstance(tags, list):
        raise ValidationError(
            message="Tags must be a list", details={"tags": str(tags), "function_name": func_name}
        )

    validated_tags = []
    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            raise ValidationError(
                message=f"Tag at index {i} must be a string",
                details={"tag_index": i, "function_name": func_name},
            )

        # Sanitize tag
        sanitized_tag = tag.strip()
        if not sanitized_tag:
            raise ValidationError(
                message=f"Tag at index {i} cannot be empty",
                details={"tag_index": i, "function_name": func_name},
            )

        validated_tags.append(sanitized_tag)

    return validated_tags


def _validate_models(
    request_model: type[BaseModel] | None,
    response_model: type[BaseModel] | None,
    func_name: str,
) -> None:
    """Validate Pydantic models."""
    if request_model and not issubclass(request_model, BaseModel):
        raise ValidationError(
            message="Request model must be a Pydantic BaseModel subclass",
            details={"request_model": str(request_model), "function_name": func_name},
        )

    if response_model and not issubclass(response_model, BaseModel):
        raise ValidationError(
            message="Response model must be a Pydantic BaseModel subclass",
            details={"response_model": str(response_model), "function_name": func_name},
        )
