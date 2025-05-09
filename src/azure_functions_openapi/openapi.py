# src/azure_functions_openapi/openapi.py
from typing import Any, Dict, List, cast
import json
import yaml

from azure_functions_openapi.decorator import get_openapi_registry


def _model_to_schema(model_cls: Any) -> Dict[str, Any]:
    """Return JSON-schema from a Pydantic v2 model class.
    Parameters:
        model_cls: Pydantic model class.
    Returns:
        Dict[str, Any]: JSON schema representation of the model.
    """
    return cast(Dict[str, Any], model_cls.model_json_schema())


def generate_openapi_spec(title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Compile an OpenAPI-3 specification from the registry.
    No base-path is added; `route=` is used exactly as provided.
    """
    registry = get_openapi_registry()
    paths: Dict[str, Dict[str, Any]] = {}

    for func_name, meta in registry.items():
        # route & method --------------------------------------------------
        path = meta.get("route") or f"/{func_name}"
        method = (meta.get("method") or "get").lower()

        # responses -------------------------------------------------------
        responses: Dict[str, Any] = {}
        for status, detail in meta.get("response", {}).items():
            resp = {"description": detail.get("description", "")}
            if "content" in detail:
                resp["content"] = detail["content"]
            responses[str(status)] = resp

        if meta.get("response_model"):
            responses["200"] = {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "schema": _model_to_schema(meta["response_model"])
                    }
                },
            }

        # operation object ------------------------------------------------
        op: Dict[str, Any] = {
            "summary": meta.get("summary", ""),
            "description": meta.get("description", ""),
            "operationId": meta.get("operation_id") or f"{method}_{func_name}",
            "tags": meta.get("tags") or ["default"],
            "responses": responses,
        }

        # parameters ------------------------------------------------------
        parameters: List[Dict[str, Any]] = meta.get("parameters", [])
        if parameters:
            op["parameters"] = parameters

        # requestBody (POST/PUT/PATCH) ------------------------------------
        if method in {"post", "put", "patch"}:
            if meta.get("request_body"):
                op["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": meta["request_body"]}},
                }
            elif meta.get("request_model"):
                op["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": _model_to_schema(meta["request_model"])
                        }
                    },
                }

        # merge into paths (support multiple methods per route) ----------
        paths.setdefault(path, {})[method] = op

    return {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "version": version,
            "description": (
                "Auto-generated OpenAPI documentation. "
                "Markdown supported in descriptions (CommonMark)."
            ),
        },
        "paths": paths,
    }


def get_openapi_json() -> str:
    """Return the spec as pretty-printed JSON (UTF-8).
    Returns:
        str: OpenAPI spec in JSON format.
    """
    return json.dumps(generate_openapi_spec(), indent=2, ensure_ascii=False)


def get_openapi_yaml() -> str:
    """Return the spec as YAML.
    Returns:
        str: OpenAPI spec in YAML format.
    """
    return yaml.safe_dump(generate_openapi_spec(), sort_keys=False, allow_unicode=True)
