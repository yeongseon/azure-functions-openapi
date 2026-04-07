from __future__ import annotations

import builtins
from collections.abc import Iterator
from dataclasses import dataclass
import importlib
from typing import Any

from pydantic import BaseModel
import pytest

from azure_functions_openapi.bridge import _model_to_parameters, scan_validation_metadata
from azure_functions_openapi.decorator import (
    _openapi_registry,
    _registry_lock,
    clear_openapi_registry,
    get_openapi_registry,
    register_openapi_metadata,
)
from azure_functions_openapi.exceptions import OpenAPISpecConfigError
from azure_functions_openapi.utils import model_to_schema, type_to_schema

try:
    validation_module = importlib.import_module("azure_functions_validation.decorator")
    RuntimeValidationMetadata = getattr(validation_module, "ValidationMetadata")
    has_validation = True
except ImportError:
    RuntimeValidationMetadata = None
    has_validation = False

if has_validation and RuntimeValidationMetadata is not None:
    ValidationMetadata = RuntimeValidationMetadata
else:

    @dataclass(frozen=True)
    class FallbackValidationMetadata:
        body: Any = None
        query: Any = None
        path: Any = None
        headers: Any = None
        response_model: Any = None

    ValidationMetadata = FallbackValidationMetadata


pytestmark = pytest.mark.skipif(
    not has_validation, reason="azure-functions-validation not installed"
)


@pytest.fixture(autouse=True)
def _clean_registry() -> Iterator[None]:
    clear_openapi_registry()
    yield
    clear_openapi_registry()


class CreateBody(BaseModel):
    name: str


class QueryModel(BaseModel):
    limit: int


class PathModel(BaseModel):
    user_id: int


class ResponseModel(BaseModel):
    id: int


class AltResponseModel(BaseModel):
    ok: bool


@dataclass
class MockBinding:
    route: str
    methods: list[str] | None
    type: str = "httpTrigger"


@dataclass
class MockFunction:
    _name: str
    _func: Any
    _bindings: list[Any]


@dataclass
class MockBuilder:
    _function: MockFunction


@dataclass
class MockApp:
    _function_builders: list[MockBuilder]


def _make_validated_handler(metadata: Any) -> Any:
    def handler(req: Any) -> Any:
        return req

    setattr(handler, "_af_validation_metadata", metadata)
    return handler


def _make_app(
    *,
    name: str = "create_user",
    route: str = "users",
    methods: list[str] | None = None,
    metadata: Any = None,
) -> MockApp:
    handler = _make_validated_handler(metadata) if metadata is not None else (lambda req: req)
    binding = MockBinding(route=route, methods=methods or ["POST"])
    fn = MockFunction(_name=name, _func=handler, _bindings=[binding])
    return MockApp(_function_builders=[MockBuilder(_function=fn)])


def test_scan_discovers_validation_metadata() -> None:
    app = _make_app(metadata=ValidationMetadata(body=CreateBody, response_model=ResponseModel))

    scan_validation_metadata(app)

    registry = get_openapi_registry()
    entry = registry["post::/api/users"]
    assert entry["response_model"] is ResponseModel
    assert "request_body" in entry


def test_scan_skips_non_validated_functions() -> None:
    app = _make_app(metadata=None)

    scan_validation_metadata(app)

    assert get_openapi_registry() == {}


def test_explicit_openapi_wins() -> None:
    register_openapi_metadata(path="/api/users", method="post", summary="explicit")
    app = _make_app(metadata=ValidationMetadata(body=CreateBody, response_model=ResponseModel))

    scan_validation_metadata(app)

    entry = get_openapi_registry()["post::/api/users"]
    assert entry["summary"] == "explicit"


def test_body_model_registered_as_request_body() -> None:
    app = _make_app(metadata=ValidationMetadata(body=CreateBody))

    scan_validation_metadata(app)

    schema = get_openapi_registry()["post::/api/users"]["request_body"]
    assert schema["type"] == "object"
    assert "name" in schema["properties"]


def test_query_model_registered_as_parameters() -> None:
    app = _make_app(metadata=ValidationMetadata(query=QueryModel))

    scan_validation_metadata(app)

    params = get_openapi_registry()["post::/api/users"]["parameters"]
    assert any(p["in"] == "query" and p["name"] == "limit" for p in params)


def test_path_model_registered_as_parameters() -> None:
    app = _make_app(route="users/{user_id}", metadata=ValidationMetadata(path=PathModel))

    scan_validation_metadata(app)

    params = get_openapi_registry()["post::/api/users/{user_id}"]["parameters"]
    path_param = next(p for p in params if p["name"] == "user_id")
    assert path_param["in"] == "path"
    assert path_param["required"] is True


def test_response_model_registered() -> None:
    app = _make_app(metadata=ValidationMetadata(response_model=ResponseModel))

    scan_validation_metadata(app)

    assert get_openapi_registry()["post::/api/users"]["response_model"] is ResponseModel


def test_import_error_without_validation_package(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def raising_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("azure_functions_validation"):
            raise ImportError("not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", raising_import)

    with pytest.raises(ImportError, match="azure-functions-validation"):
        scan_validation_metadata(MockApp(_function_builders=[]))


def test_scan_empty_app() -> None:
    scan_validation_metadata(MockApp(_function_builders=[]))
    assert get_openapi_registry() == {}


def test_model_to_parameters_conversion() -> None:
    params = _model_to_parameters(QueryModel, "query")
    limit = next(p for p in params if p["name"] == "limit")
    assert limit["in"] == "query"
    assert limit["schema"]["type"] == "integer"


def test_conflict_detection() -> None:
    register_openapi_metadata(path="/api/users", method="post", response_model=AltResponseModel)
    app = _make_app(metadata=ValidationMetadata(response_model=ResponseModel))

    with pytest.raises(OpenAPISpecConfigError):
        scan_validation_metadata(app)


def test_scan_skips_non_http_bindings() -> None:
    handler = _make_validated_handler(ValidationMetadata(body=CreateBody))
    fn = MockFunction(
        _name="non_http",
        _func=handler,
        _bindings=[MockBinding(route="queue", methods=None, type="queueTrigger")],
    )
    app = MockApp(_function_builders=[MockBuilder(_function=fn)])

    scan_validation_metadata(app)

    assert get_openapi_registry() == {}


def test_scan_defaults_method_to_get_when_unspecified() -> None:
    handler = _make_validated_handler(ValidationMetadata(response_model=ResponseModel))
    binding = MockBinding(route="users", methods=None, type="httpTrigger")
    fn = MockFunction(_name="get_users", _func=handler, _bindings=[binding])
    app = MockApp(_function_builders=[MockBuilder(_function=fn)])

    scan_validation_metadata(app)

    assert "get::/api/users" in get_openapi_registry()


def test_scan_merges_explicit_function_name_entry() -> None:
    with _registry_lock:
        _openapi_registry["create_user"] = {
            "summary": "explicit",
            "description": "",
            "tags": ["default"],
            "operation_id": "create_user",
            "route": "/api/users",
            "method": "post",
            "parameters": [],
            "security": [],
            "security_scheme": {},
            "request_model": None,
            "request_body": None,
            "request_body_required": True,
            "response_model": None,
            "response": {},
            "function_name": "create_user",
            "_function_id": "tests.create_user",
        }

    app = _make_app(name="create_user", metadata=ValidationMetadata(body=CreateBody))
    scan_validation_metadata(app)

    entry = get_openapi_registry()["create_user"]
    assert entry["summary"] == "explicit"
    assert entry["request_body"]["type"] == "object"


def test_parameter_conflict_detection() -> None:
    register_openapi_metadata(
        path="/api/users",
        method="post",
        parameters=[
            {"name": "limit", "in": "query", "required": True, "schema": {"type": "string"}}
        ],
    )
    app = _make_app(metadata=ValidationMetadata(query=QueryModel))

    with pytest.raises(OpenAPISpecConfigError, match="Conflicting validation"):
        scan_validation_metadata(app)


def test_type_to_schema_registers_defs_for_generic_types() -> None:
    components: dict[str, Any] = {"schemas": {}}

    schema = type_to_schema(list[ResponseModel], components)

    assert schema["type"] == "array"
    assert schema["items"]["$ref"] == "#/components/schemas/ResponseModel"
    assert "ResponseModel" in components["schemas"]


def test_model_to_schema_accepts_generic_type_hints() -> None:
    components: dict[str, Any] = {"schemas": {}}

    schema = model_to_schema(list[ResponseModel], components)

    assert schema["type"] == "array"
    assert schema["items"]["$ref"] == "#/components/schemas/ResponseModel"


def test_type_to_schema_without_components() -> None:
    schema = type_to_schema(ResponseModel | None)
    assert "anyOf" in schema or "oneOf" in schema or "type" in schema
