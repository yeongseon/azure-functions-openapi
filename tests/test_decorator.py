# tests/test_decorator.py

import azure.functions as func
from azure.functions.decorators.function_app import FunctionBuilder

import azure_functions_openapi.decorator as decorator_module
from azure_functions_openapi.decorator import get_openapi_registry, openapi
from azure_functions_openapi.openapi import generate_openapi_spec


def _clear_registry() -> None:
    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()


def test_openapi_registers_metadata() -> None:
    @openapi(
        summary="Test Summary",
        description="Detailed test description",
        response={200: {"description": "OK"}},
        parameters=[
            {
                "name": "q",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Optional query string",
            }
        ],
    )
    def dummy_function() -> None:
        pass

    registry = get_openapi_registry()
    assert "dummy_function" in registry
    assert registry["dummy_function"]["summary"] == "Test Summary"
    assert registry["dummy_function"]["description"] == "Detailed test description"
    assert 200 in registry["dummy_function"]["response"]

    # Check parameters metadata
    parameters = registry["dummy_function"].get("parameters")
    assert isinstance(parameters, list)
    assert parameters[0]["name"] == "q"
    assert parameters[0]["in"] == "query"
    assert parameters[0]["required"] is False
    assert parameters[0]["schema"]["type"] == "string"
    assert parameters[0]["description"] == "Optional query string"


def test_openapi_registers_metadata_with_request_body() -> None:
    @openapi(
        summary="Test with body",
        description="Test endpoint with request body",
        response={201: {"description": "Created"}},
        parameters=[],
        request_body={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        },
    )
    def dummy_with_body() -> None:
        pass

    registry = get_openapi_registry()
    assert "dummy_with_body" in registry
    assert "request_body" in registry["dummy_with_body"]
    schema = registry["dummy_with_body"]["request_body"]
    assert schema["type"] == "object"
    assert "name" in schema["properties"]
    assert schema["properties"]["name"]["type"] == "string"


def test_openapi_registers_security_metadata() -> None:
    @openapi(
        summary="Secured endpoint",
        security=[{"BearerAuth": []}],
    )
    def secured_dummy() -> None:
        pass

    registry = get_openapi_registry()
    assert registry["secured_dummy"]["security"] == [{"BearerAuth": []}]


def test_openapi_accepts_function_builder_when_decorator_is_outermost() -> None:
    _clear_registry()
    app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

    @openapi(summary="Hello", description="Returns plain text.")
    @app.route(route="hello")
    def hello(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse("Hello", status_code=200)

    assert isinstance(hello, FunctionBuilder)

    registry = get_openapi_registry()
    assert registry["hello"]["summary"] == "Hello"
    assert registry["hello"]["description"] == "Returns plain text."

    spec = generate_openapi_spec()
    assert "/hello" in spec["paths"]


def test_openapi_keeps_function_builder_chain_intact() -> None:
    _clear_registry()
    app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

    @app.function_name(name="hello_alias")
    @openapi(summary="Hello")
    @app.route(route="hello")
    def hello(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse("Hello", status_code=200)

    assert isinstance(hello, FunctionBuilder)
    built = app._function_builders[0].build(app.auth_level)

    assert built.get_function_name() == "hello_alias"
