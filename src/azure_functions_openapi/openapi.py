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

        # If response_model is specified, override or enrich the 200 response
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

        # Use provided tags or default
        tags = metadata.get("tags") or ["default"]

        operation: Dict[str, Any] = {
            "summary": metadata.get("summary", ""),
            "description": metadata.get("description", ""),
            "operationId": operation_id,
            "tags": tags,
            "responses": responses,
        }

        if metadata.get("parameters"):
            operation["parameters"] = metadata["parameters"]

        if metadata.get("request_body"):
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": metadata["request_body"]}},
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
        "info": {"title": title, "version": version},
        "paths": paths,
    }


def get_openapi_json() -> str:
    """
    Return the OpenAPI JSON string for HTTP response.
    """
    spec = generate_openapi_spec()
    return json.dumps(spec, indent=2)
