# src/azure_functions_openapi/openapi.py
from __future__ import annotations

import json
import logging
from typing import Any

import yaml

from azure_functions_openapi.cache import cached_openapi_spec
from azure_functions_openapi.decorator import get_openapi_registry
from azure_functions_openapi.errors import OpenAPIError
from azure_functions_openapi.utils import model_to_schema

logger = logging.getLogger(__name__)


OPENAPI_VERSION_3_0 = "3.0.0"
OPENAPI_VERSION_3_1 = "3.1.0"


def _convert_nullable_to_type_array(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert OpenAPI 3.0 nullable to 3.1 type array syntax."""
    result = schema.copy()

    if result.get("nullable") is True and "type" in result:
        original_type = result["type"]
        if isinstance(original_type, str):
            result["type"] = [original_type, "null"]
        elif isinstance(original_type, list) and "null" not in original_type:
            result["type"] = original_type + ["null"]
        del result["nullable"]

    return result


def _convert_schema_to_3_1(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively convert a schema from OpenAPI 3.0 to 3.1 format."""
    if not isinstance(schema, dict):
        return schema

    result = _convert_nullable_to_type_array(schema)

    if "example" in result and "examples" not in result:
        result["examples"] = [result.pop("example")]

    if "properties" in result:
        result["properties"] = {
            k: _convert_schema_to_3_1(v) for k, v in result["properties"].items()
        }

    if "items" in result:
        result["items"] = _convert_schema_to_3_1(result["items"])

    if "allOf" in result:
        result["allOf"] = [_convert_schema_to_3_1(s) for s in result["allOf"]]

    if "anyOf" in result:
        result["anyOf"] = [_convert_schema_to_3_1(s) for s in result["anyOf"]]

    if "oneOf" in result:
        result["oneOf"] = [_convert_schema_to_3_1(s) for s in result["oneOf"]]

    if "additionalProperties" in result and isinstance(result["additionalProperties"], dict):
        result["additionalProperties"] = _convert_schema_to_3_1(result["additionalProperties"])

    return result


def _convert_schemas_to_3_1(schemas: dict[str, Any]) -> dict[str, Any]:
    """Convert all schemas in components to OpenAPI 3.1 format."""
    return {name: _convert_schema_to_3_1(schema) for name, schema in schemas.items()}


def generate_openapi_spec(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = OPENAPI_VERSION_3_0,
) -> dict[str, Any]:
    """
    Compile an OpenAPI specification from the registry.

    Parameters:
        title: API title
        version: API version
        openapi_version: OpenAPI specification version ("3.0.0" or "3.1.0")

    Returns:
        OpenAPI specification dictionary
    """
    if openapi_version not in (OPENAPI_VERSION_3_0, OPENAPI_VERSION_3_1):
        raise OpenAPIError(
            message=f"Unsupported OpenAPI version: {openapi_version}",
            details={"supported_versions": [OPENAPI_VERSION_3_0, OPENAPI_VERSION_3_1]},
        )

    try:
        registry = get_openapi_registry()
        paths: dict[str, dict[str, Any]] = {}
        components: dict[str, Any] = {"schemas": {}}

        for func_name, meta in registry.items():
            try:
                # route & method --------------------------------------------------
                path = meta.get("route") or f"/{func_name}"
                method = (meta.get("method") or "get").lower()

                # responses -------------------------------------------------------
                responses: dict[str, Any] = {}
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
                op: dict[str, Any] = {
                    "summary": meta.get("summary", ""),
                    "description": meta.get("description", ""),
                    "operationId": meta.get("operation_id") or f"{method}_{func_name}",
                    "tags": meta.get("tags") or ["default"],
                    "responses": responses,
                }

                # parameters ------------------------------------------------------
                parameters: list[dict[str, Any]] = meta.get("parameters", [])
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

        spec: dict[str, Any] = {
            "openapi": openapi_version,
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

        if openapi_version == OPENAPI_VERSION_3_1:
            spec["info"]["summary"] = title

        if components.get("schemas"):
            if openapi_version == OPENAPI_VERSION_3_1:
                components["schemas"] = _convert_schemas_to_3_1(components["schemas"])
            spec["components"] = components

        logger.info(
            f"Generated OpenAPI {openapi_version} spec with {len(paths)} paths "
            f"for {len(registry)} functions"
        )
        return spec

    except Exception as e:
        logger.error(f"Failed to generate OpenAPI specification: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI specification", details={"error": str(e)}, cause=e
        )


def get_openapi_json(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = OPENAPI_VERSION_3_0,
) -> str:
    """Return the spec as pretty-printed JSON (UTF-8).

    Parameters:
        title: API title
        version: API version
        openapi_version: OpenAPI specification version ("3.0.0" or "3.1.0")

    Returns:
        OpenAPI spec in JSON format.
    """
    try:
        spec = cached_openapi_spec(title, version, openapi_version)
        return json.dumps(spec, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI JSON: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI JSON", details={"error": str(e)}, cause=e
        )


def get_openapi_yaml(
    title: str = "API",
    version: str = "1.0.0",
    openapi_version: str = OPENAPI_VERSION_3_0,
) -> str:
    """Return the spec as YAML.

    Parameters:
        title: API title
        version: API version
        openapi_version: OpenAPI specification version ("3.0.0" or "3.1.0")

    Returns:
        OpenAPI spec in YAML format.
    """
    try:
        spec = cached_openapi_spec(title, version, openapi_version)
        return yaml.safe_dump(spec, sort_keys=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI YAML: {str(e)}")
        raise OpenAPIError(
            message="Failed to generate OpenAPI YAML", details={"error": str(e)}, cause=e
        )
