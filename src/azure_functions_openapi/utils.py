# src/azure_functions_openapi/utils.py
import re
from typing import Any, Dict, cast

from packaging import version
import pydantic

PYDANTIC_V2 = version.parse(pydantic.__version__) >= version.parse("2.0.0")


def model_to_schema(model_cls: Any) -> Dict[str, Any]:
    """Return JSON schema from a Pydantic model class.
    Parameters:
        model_cls: Pydantic model class.
    Returns:
        Dict[str, Any]: JSON schema representation of the model.
    """

    if PYDANTIC_V2:
        return cast(Dict[str, Any], model_cls.model_json_schema())
    return cast(Dict[str, Any], model_cls.schema())


def validate_route_path(route: str) -> bool:
    """Validate route path format for security.
    
    Parameters:
        route: Route path to validate.
    Returns:
        bool: True if route is valid, False otherwise.
    """
    if not route or not isinstance(route, str):
        return False
    
    # Check for dangerous patterns
    dangerous_patterns = [
        r'\.\.',  # Path traversal
        r'<script',  # XSS attempts
        r'javascript:',  # JavaScript injection
        r'data:',  # Data URI injection
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, route, re.IGNORECASE):
            return False
    
    # Route should start with / and contain only safe characters
    if not route.startswith('/'):
        return False
    
    # Allow alphanumeric, hyphens, underscores, slashes, and curly braces for path parameters
    if not re.match(r'^/[a-zA-Z0-9_\-/{}\s]*$', route):
        return False
    
    return True


def sanitize_operation_id(operation_id: str) -> str:
    """Sanitize operation ID to prevent injection attacks.
    
    Parameters:
        operation_id: Operation ID to sanitize.
    Returns:
        str: Sanitized operation ID.
    """
    if not operation_id or not isinstance(operation_id, str):
        return ""
    
    # Remove dangerous characters and keep only alphanumeric and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', operation_id)
    
    # Ensure it starts with a letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = 'op_' + sanitized
    
    return sanitized
