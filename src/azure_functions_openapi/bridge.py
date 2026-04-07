from __future__ import annotations

from collections.abc import Iterable
import logging
from typing import Any, get_origin

from pydantic import BaseModel

from azure_functions_openapi.decorator import (
    _openapi_registry,
    _registry_lock,
    register_openapi_metadata,
)
from azure_functions_openapi.exceptions import OpenAPISpecConfigError
from azure_functions_openapi.utils import type_to_schema

logger = logging.getLogger(__name__)


def _is_base_model_type(model: Any) -> bool:
    return isinstance(model, type) and issubclass(model, BaseModel)


def _normalize_method(method: Any) -> str:
    if method is None:
        return "get"
    value = getattr(method, "value", method)
    return str(value).lower()


def _normalize_path(route: str | None, function_name: str) -> str:
    raw = (route or function_name or "").strip()
    if not raw:
        raw = function_name
    if not raw.startswith("/"):
        raw = f"/{raw}"
    if raw == "/api" or raw.startswith("/api/"):
        return raw
    if raw.startswith("/api/"):
        return raw
    if raw.startswith("/api") and len(raw) > 4 and raw[4] == "/":
        return raw
    return f"/api{raw}"


def _extract_http_binding(function_obj: Any) -> Any | None:
    for binding in getattr(function_obj, "_bindings", []):
        if str(getattr(binding, "type", "")).lower() == "httptrigger":
            return binding
    return None


def _extract_methods(binding: Any) -> list[str]:
    methods = getattr(binding, "methods", None)
    if methods is None:
        return ["get"]
    if isinstance(methods, str):
        return [_normalize_method(methods)]
    if isinstance(methods, Iterable):
        normalized = [_normalize_method(item) for item in methods]
        return normalized or ["get"]
    return ["get"]


def _merge_parameters(
    existing: list[dict[str, Any]],
    discovered: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = list(existing)
    index_by_key: dict[tuple[str, str], int] = {
        (str(item.get("in", "")), str(item.get("name", ""))): i
        for i, item in enumerate(existing)
        if isinstance(item, dict)
    }
    for param in discovered:
        key = (str(param.get("in", "")), str(param.get("name", "")))
        if key not in index_by_key:
            index_by_key[key] = len(merged)
            merged.append(param)
            continue
        current = merged[index_by_key[key]]
        if current != param:
            raise OpenAPISpecConfigError(
                "Conflicting parameter schema for "
                f"'{key[0]}:{key[1]}' discovered from validation metadata"
            )
    return merged


def _models_conflict(existing: dict[str, Any], discovered: dict[str, Any]) -> bool:
    existing_response = existing.get("response_model")
    discovered_response = discovered.get("response_model")
    if (
        existing_response is not None
        and discovered_response is not None
        and existing_response is not discovered_response
    ):
        return True

    existing_request_body = existing.get("request_body")
    discovered_request_body = discovered.get("request_body")
    if (
        existing_request_body is not None
        and discovered_request_body is not None
        and existing_request_body != discovered_request_body
    ):
        return True

    try:
        _merge_parameters(existing.get("parameters", []), discovered.get("parameters", []))
    except OpenAPISpecConfigError:
        return True

    return False


def _merge_into_existing(existing: dict[str, Any], discovered: dict[str, Any]) -> None:
    if _models_conflict(existing, discovered):
        raise OpenAPISpecConfigError("Conflicting validation and OpenAPI models for endpoint")

    if not existing.get("request_body") and discovered.get("request_body"):
        existing["request_body"] = discovered["request_body"]

    if not existing.get("response_model") and discovered.get("response_model"):
        existing["response_model"] = discovered["response_model"]

    existing_params = existing.get("parameters", [])
    discovered_params = discovered.get("parameters", [])
    existing["parameters"] = _merge_parameters(existing_params, discovered_params)


def _field_type_to_schema(annotation: Any) -> dict[str, Any]:
    origin = get_origin(annotation)
    if annotation is str:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    if origin in (list, tuple, set):
        return {"type": "array"}
    schema = type_to_schema(annotation)
    if "$defs" in schema:
        schema = dict(schema)
        schema.pop("$defs", None)
    return schema


def _model_to_parameters(model_cls: type, location: str) -> list[dict[str, Any]]:
    if not hasattr(model_cls, "model_fields"):
        raise TypeError(
            f"Expected Pydantic model with model_fields, got {type(model_cls).__name__}"
        )

    required_fields = getattr(model_cls, "model_fields", {})
    required_names = {
        name
        for name, field in required_fields.items()
        if getattr(field, "is_required", lambda: False)()
    }
    params: list[dict[str, Any]] = []
    for name, field in required_fields.items():
        schema = _field_type_to_schema(getattr(field, "annotation", Any))
        params.append(
            {
                "name": name,
                "in": location,
                "required": location == "path" or name in required_names,
                "schema": schema,
            }
        )
    return params


def _discovered_operation(
    function_name: str, metadata: Any, path: str, method: str
) -> dict[str, Any]:
    request_body = (
        type_to_schema(metadata.body) if getattr(metadata, "body", None) is not None else None
    )
    parameters: list[dict[str, Any]] = []
    if getattr(metadata, "query", None) is not None:
        parameters.extend(_model_to_parameters(metadata.query, "query"))
    if getattr(metadata, "path", None) is not None:
        parameters.extend(_model_to_parameters(metadata.path, "path"))
    if getattr(metadata, "headers", None) is not None:
        parameters.extend(_model_to_parameters(metadata.headers, "header"))
    return {
        "function_name": function_name,
        "route": path,
        "method": method,
        "request_body": request_body,
        "parameters": parameters,
        "response_model": getattr(metadata, "response_model", None),
    }


def scan_validation_metadata(app: Any) -> None:
    try:
        from azure_functions_validation.decorator import ValidationMetadata
    except ImportError as exc:
        raise ImportError(
            "scan_validation_metadata() requires optional dependency 'azure-functions-validation'. "
            "Install with: pip install azure-functions-openapi[bridge]"
        ) from exc

    builders = getattr(app, "_function_builders", None)
    if not builders:
        logger.debug("No function builders found on app; skipping validation scan")
        return

    for builder in builders:
        function_obj = getattr(builder, "_function", None)
        if function_obj is None:
            continue
        function_name = str(getattr(function_obj, "_name", ""))
        handler = getattr(function_obj, "_func", None)
        if handler is None:
            continue
        metadata = getattr(handler, "_af_validation_metadata", None)
        if not isinstance(metadata, ValidationMetadata):
            continue

        binding = _extract_http_binding(function_obj)
        if binding is None:
            logger.debug(
                "Function '%s' has validation metadata but is not HTTP triggered", function_name
            )
            continue

        path = _normalize_path(getattr(binding, "route", None), function_name)
        methods = _extract_methods(binding)

        for method in methods:
            discovered = _discovered_operation(function_name, metadata, path, method)
            endpoint_key = f"{method}::{path}"

            with _registry_lock:
                explicit_by_name = _openapi_registry.get(function_name)
                explicit_by_endpoint = _openapi_registry.get(endpoint_key)

                if explicit_by_name is not None:
                    _merge_into_existing(explicit_by_name, discovered)
                    logger.debug(
                        "Merged validation metadata into explicit @openapi entry '%s'",
                        function_name,
                    )
                    continue

                if explicit_by_endpoint is not None:
                    _merge_into_existing(explicit_by_endpoint, discovered)
                    logger.debug(
                        "Merged validation metadata into explicit OpenAPI endpoint '%s'",
                        endpoint_key,
                    )
                    continue

            register_openapi_metadata(
                path=path,
                method=method,
                request_body=discovered.get("request_body"),
                response_model=discovered.get("response_model")
                if _is_base_model_type(discovered.get("response_model"))
                else None,
                parameters=discovered.get("parameters") or None,
            )
            logger.debug("Registered validation metadata for endpoint '%s'", endpoint_key)
