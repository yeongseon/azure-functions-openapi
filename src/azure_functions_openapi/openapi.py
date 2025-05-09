# src/azure_functions_openapi/openapi.py
from typing import Dict, Any
from azure_functions_openapi.decorator import get_openapi_registry
import json
import yaml


def generate_openapi_spec(title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Generate OpenAPI 3.0 specification from all registered function metadata.

    Parameters:
        title: The title of the API.
        version: The API version string.

    Returns:
        A dictionary representing the full OpenAPI specification.
    """
    registry = get_openapi_registry()
    paths: Dict[str, Any] = {}

    for func_name, metadata in registry.items():
        # Ensure path is not None
        path = metadata.get("route") or f"/{func_name}"
        method = (metadata.get("method") or "get").lower()

        # Build responses
        responses: Dict[str, Any] = {}
        for code, response_detail in metadata.get("response", {}).items():
            resp_obj: Dict[str, Any] = {
                "description": response_detail.get("description", "")
            }
            if "content" in response_detail:
                resp_obj["content"] = response_detail["content"]
            responses[str(code)] = resp_obj

        if metadata.get("response_model"):
            schema = metadata["response_model"].model_json_schema()
            responses["200"] = {
                "description": "Successful Response",
                "content": {"application/json": {"schema": schema}},
            }

        # Auto-generate operationId if not provided
        operation_id = metadata.get("operation_id")
        if not operation_id:
            normalized_path = (
                path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            )
            operation_id = f"{method}_{normalized_path or 'root'}"

        tags = metadata.get("tags") or ["default"]

        operation: Dict[str, Any] = {
            "summary": metadata.get("summary", ""),
            "description": metadata.get("description", ""),
            "operationId": operation_id,
            "tags": tags,
            "responses": responses,
        }

        # Add query parameters (e.g., ?name=Azure)
        parameters = metadata.get("parameters", [])
        if method == "get":
            if "name" not in [param.get("name") for param in parameters]:
                parameters.append(
                    {
                        "name": "name",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Name to greet",
                    }
                )
        if parameters:
            operation["parameters"] = parameters

        # Only include requestBody for methods that allow it
        if method in {"post", "put", "patch"}:
            if metadata.get("request_body"):
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {"schema": metadata["request_body"]}
                    },
                }
            elif metadata.get("request_model"):
                schema = metadata["request_model"].model_json_schema()
                operation["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": schema}},
                }

        paths[path] = {method: operation}

    return {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "version": version,
            "description": "Auto-generated OpenAPI documentation.\nSupports Markdown in descriptions (CommonMark).",
        },
        "paths": paths,
    }


def get_openapi_json() -> str:
    spec = generate_openapi_spec()
    return json.dumps(spec, indent=2)


def get_openapi_yaml() -> str:
    spec = generate_openapi_spec()
    return yaml.dump(spec, sort_keys=False, allow_unicode=True)
