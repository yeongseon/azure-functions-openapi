# src/azure_functions_openapi/utils.py
import re
from typing import Any, Dict, List, Optional, Tuple, cast

from packaging import version
import pydantic

PYDANTIC_V2 = version.parse(pydantic.__version__) >= version.parse("2.0.0")


def _rewrite_ref(ref: str) -> str:
    if ref.startswith("#/$defs/"):
        return ref.replace("#/$defs/", "#/components/schemas/")
    if ref.startswith("#/definitions/"):
        return ref.replace("#/definitions/", "#/components/schemas/")
    return ref


def _rewrite_refs(obj: Any) -> Any:
    if isinstance(obj, dict):
        rewritten: Dict[str, Any] = {}
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                rewritten[key] = _rewrite_ref(value)
            else:
                rewritten[key] = _rewrite_refs(value)
        return rewritten
    if isinstance(obj, list):
        return [_rewrite_refs(item) for item in obj]
    return obj


def _pop_definitions(schema: Dict[str, Any]) -> Dict[str, Any]:
    definitions: Dict[str, Any] = {}
    for key in ("$defs", "definitions"):
        value = schema.pop(key, None)
        if isinstance(value, dict):
            definitions.update(value)
    return definitions


def _collect_schemas(schema: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    normalized = cast(Dict[str, Any], _rewrite_refs(schema))
    definitions = _pop_definitions(normalized)
    collected: Dict[str, Dict[str, Any]] = {}

    queue: List[Tuple[str, Any]] = list(definitions.items())
    while queue:
        name, definition = queue.pop(0)
        if not isinstance(definition, dict):
            continue
        definition = cast(Dict[str, Any], _rewrite_refs(definition))
        nested = _pop_definitions(definition)
        if nested:
            queue.extend(list(nested.items()))
        collected[name] = definition

    return normalized, collected


def _resolve_name_collision(
    name: str,
    schema: Dict[str, Any],
    existing: Dict[str, Dict[str, Any]],
) -> str:
    if name not in existing:
        return name
    if existing[name] == schema:
        return name
    index = 2
    while True:
        candidate = f"{name}_{index}"
        if candidate not in existing:
            return candidate
        if existing[candidate] == schema:
            return candidate
        index += 1


def _rewrite_refs_with_map(obj: Any, name_map: Dict[str, str]) -> Any:
    if not name_map:
        return obj
    if isinstance(obj, dict):
        rewritten: Dict[str, Any] = {}
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                if value.startswith("#/components/schemas/"):
                    ref_name = value.split("#/components/schemas/", 1)[1]
                    if ref_name in name_map:
                        rewritten[key] = f"#/components/schemas/{name_map[ref_name]}"
                        continue
                rewritten[key] = value
            else:
                rewritten[key] = _rewrite_refs_with_map(value, name_map)
        return rewritten
    if isinstance(obj, list):
        return [_rewrite_refs_with_map(item, name_map) for item in obj]
    return obj


def model_to_schema(model_cls: Any, components: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return OpenAPI schema from a Pydantic model class.
    Parameters:
        model_cls: Pydantic model class.
        components: OpenAPI components dict to register schemas.
    Returns:
        Dict[str, Any]: Schema with $ref to components.schemas.
    """

    if PYDANTIC_V2:
        schema = cast(
            Dict[str, Any],
            model_cls.model_json_schema(ref_template="#/components/schemas/{model}"),
        )
    else:
        schema = cast(
            Dict[str, Any],
            model_cls.schema(ref_template="#/components/schemas/{model}"),
        )

    if components is None:
        components = {}
    schemas = components.setdefault("schemas", {})

    normalized, definitions = _collect_schemas(schema)
    local_schemas: Dict[str, Dict[str, Any]] = {model_cls.__name__: normalized}
    local_schemas.update(definitions)

    name_map: Dict[str, str] = {}
    for name, local_schema in local_schemas.items():
        resolved_name = _resolve_name_collision(name, local_schema, schemas)
        if resolved_name != name:
            name_map[name] = resolved_name

    if name_map:
        updated_local_schemas: Dict[str, Dict[str, Any]] = {}
        for name, local_schema in local_schemas.items():
            final_name = name_map.get(name, name)
            rewritten_schema = cast(Dict[str, Any], _rewrite_refs_with_map(local_schema, name_map))
            updated_local_schemas[final_name] = rewritten_schema
        local_schemas = updated_local_schemas

    for name, local_schema in local_schemas.items():
        if name not in schemas or schemas[name] != local_schema:
            schemas[name] = local_schema

    root_name = name_map.get(model_cls.__name__, model_cls.__name__)
    return {"$ref": f"#/components/schemas/{root_name}"}


def validate_route_path(route: Any) -> bool:
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


def sanitize_operation_id(operation_id: Any) -> str:
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
