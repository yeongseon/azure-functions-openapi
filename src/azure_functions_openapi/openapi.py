# src/azure_functions_openapi/openapi.py
import json
import logging
from typing import Any, Dict, List

import yaml

from azure_functions_openapi.cache import (
    cached_openapi_spec,
)
from azure_functions_openapi.decorator import get_openapi_registry
from azure_functions_openapi.errors import OpenAPIError
from azure_functions_openapi.utils import model_to_schema

logger = logging.getLogger(__name__)


def generate_openapi_spec(title: str = "API", version: str = "1.0.0") -> Dict[str, Any]:
    """
    Compile an OpenAPI-3 specification from the registry.
    No base-path is added; `route=` is used exactly as provided.
    """
    try:
        registry = get_openapi_registry()
        paths: Dict[str, Dict[str, Any]] = {}
        components: Dict[str, Any] = {"schemas": {}}

        for func_name, meta in registry.items():
            try:
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
                    try:
                        responses["200"] = {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": model_to_schema(meta["response_model"], components)
                                }
                            },
                        }
                    except Exception as e:
                        logger.warning(
                            f"Failed to generate response schema for {func_name}: {str(e)}"
                        )
                        responses["200"] = {
                            "description": "Successful Response",
                            "content": {"application/json": {"schema": {"type": "object"}}},
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
                        try:
                            op["requestBody"] = {
                                "required": True,
                                "content": {
                                    "application/json": {
                                        "schema": model_to_schema(meta["request_model"], components)
                                    }
                                },
                            }
                        except Exception as e:
                            logger.warning(
                                f"Failed to generate request schema for {func_name}: {str(e)}"
                            )
                            op["requestBody"] = {
                                "required": True,
                                "content": {"application/json": {"schema": {"type": "object"}}},
                            }

                # merge into paths (support multiple methods per route) ----------
                paths.setdefault(path, {})[method] = op

            except Exception as e:
                logger.error(f"Failed to process function {func_name}: {str(e)}")
                # Continue processing other functions
                continue

        spec: Dict[str, Any] = {
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
        if components.get("schemas"):
            spec["components"] = components

        logger.info(f"Generated OpenAPI spec with {len(paths)} paths for {len(registry)} functions")
        return spec

    except Exception as e:
        logger.error(f"Failed to generate OpenAPI specification: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI specification", details={"error": str(e)}, cause=e
        )


def get_openapi_json(title: str = "API", version: str = "1.0.0") -> str:
    """Return the spec as pretty-printed JSON (UTF-8).
    Returns:
        str: OpenAPI spec in JSON format.
    """
    try:
        spec = cached_openapi_spec(title, version)
        return json.dumps(spec, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI JSON: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI JSON", details={"error": str(e)}, cause=e
        )


def get_openapi_yaml(title: str = "API", version: str = "1.0.0") -> str:
    """Return the spec as YAML.
    Returns:
        str: OpenAPI spec in YAML format.
    """
    try:
        spec = cached_openapi_spec(title, version)
        return yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI YAML: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI YAML", details={"error": str(e)}, cause=e
        )
