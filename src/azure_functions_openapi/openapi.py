# src/azure_functions_openapi/openapi.py
from typing import Dict, Any
from azure_functions_openapi.decorator import get_openapi_registry
import json


def generate_openapi_spec(title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
    registry = get_openapi_registry()
    paths: Dict[str, Any] = {}

    for func_name, metadata in registry.items():
        # Use provided route/method or fallback
        path = metadata.get("route") or f"/{func_name}"
        method = (metadata.get("method") or "get").lower()

        # Build the responses with support for description + content
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

        if metadata.get("parameters"):
            operation["parameters"] = metadata["parameters"]

        if metadata.get("request_body"):
            operation["requestBody"] = {
                "required": True,
                "content": {"application/json": {"schema": metadata["request_body"]}},
            }

        paths.setdefault(path, {})[method] = operation

    return {
        "openapi": "3.0.0",
        "info": {"title": title, "version": version},
        "paths": paths,
    }


def get_openapi_json() -> str:
    spec = generate_openapi_spec()
    return json.dumps(spec, indent=2)
