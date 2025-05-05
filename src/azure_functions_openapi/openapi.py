# src/azure_functions_openapi/openapi.py
from typing import Dict, Any
from azure_functions_openapi.decorator import get_openapi_registry
import json


def generate_openapi_spec(title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Generate OpenAPI 3.0 specification from the registered metadata.

    :param title: API title
    :param version: API version
    :return: Dictionary representing OpenAPI spec
    """
    registry = get_openapi_registry()
    paths = {}

    for func_name, metadata in registry.items():
        # NOTE: Path and method are hardcoded in MVP; will be inferred later
        path = f"/{func_name}"
        method = "get"

        # Build the responses with support for description + content (schema + examples)
        responses = {}
        for code, response_detail in metadata["response"].items():
            responses[str(code)] = {
                "description": response_detail.get("description", "")
            }
            if "content" in response_detail:
                responses[str(code)]["content"] = response_detail["content"]

        operation: Dict[str, Any] = {
            "summary": metadata["summary"],
            "description": metadata["description"],
            "responses": responses,
        }

        # Add parameters if present
        if metadata.get("parameters"):
            operation["parameters"] = metadata["parameters"]

        # Add request body if present
        if metadata.get("request_body"):
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": metadata["request_body"]}},
            }

        paths[path] = {method: operation}

    return {
        "openapi": "3.0.0",
        "info": {"title": title, "version": version},
        "paths": paths,
    }


def get_openapi_json() -> str:
    """
    Return the OpenAPI JSON string for HTTP response.
    """
    spec = generate_openapi_spec()
    return json.dumps(spec, indent=2)
