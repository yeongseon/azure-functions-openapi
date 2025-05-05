# tests/test_openapi.py
from pydantic import BaseModel
from azure_functions_openapi.openapi import generate_openapi_spec, get_openapi_json
from azure_functions_openapi.decorator import openapi, get_openapi_registry
import json


def test_generate_openapi_spec_structure():
    @openapi(
        summary="Sample summary",
        description="Sample description",
        response={200: {"description": "Success"}},
        parameters=[
            {
                "name": "q",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Optional query string",
            }
        ],
        route="/sample_func",
    )
    def sample_func():
        pass

    registry = get_openapi_registry()
    assert "sample_func" in registry

    spec = generate_openapi_spec(title="My API", version="1.2.3")

    assert spec["openapi"] == "3.0.0"
    assert spec["info"]["title"] == "My API"
    assert spec["info"]["version"] == "1.2.3"
    assert "/sample_func" in spec["paths"]
    get_op = spec["paths"]["/sample_func"]["get"]
    assert get_op["summary"] == "Sample summary"
    assert get_op["parameters"][0]["name"] == "q"
    assert get_op["parameters"][0]["in"] == "query"
    assert get_op["parameters"][0]["required"] is False
    assert get_op["parameters"][0]["schema"]["type"] == "string"
    assert get_op["parameters"][0]["description"] == "Optional query string"


def test_get_openapi_json_output():
    json_str = get_openapi_json()
    data = json.loads(json_str)

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert isinstance(data["paths"], dict)


def test_generate_openapi_spec_with_request_body():
    @openapi(
        summary="With Body",
        description="Endpoint with request body",
        response={200: {"description": "OK"}},
        route="/func_with_body",
    )
    def func_with_body():
        pass

    registry = get_openapi_registry()
    registry["func_with_body"]["request_body"] = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["username", "password"],
    }

    spec = generate_openapi_spec()
    request_body = spec["paths"]["/func_with_body"]["get"]["requestBody"]
    assert "application/json" in request_body["content"]
    schema = request_body["content"]["application/json"]["schema"]
    assert "username" in schema["properties"]
    assert "password" in schema["properties"]


def test_response_schema_and_examples():
    @openapi(
        summary="Greet user",
        description="Returns a greeting message.",
        response={
            200: {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                        "examples": {
                            "sample": {
                                "summary": "A sample response",
                                "value": {"message": "Hello, Azure!"},
                            }
                        },
                    }
                },
            }
        },
        route="/greet",
    )
    def greet():
        pass

    spec = generate_openapi_spec()
    op = spec["paths"]["/greet"]["get"]
    assert (
        op["responses"]["200"]["content"]["application/json"]["examples"]["sample"][
            "value"
        ]["message"]
        == "Hello, Azure!"
    )


def test_generate_openapi_spec_with_route_and_method():
    @openapi(
        summary="Test with custom route/method",
        description="Checks that route and method are reflected",
        response={200: {"description": "OK"}},
        route="/custom-path",
        method="post",
    )
    def custom_func():
        pass

    spec = generate_openapi_spec()
    assert "/custom-path" in spec["paths"]
    assert "post" in spec["paths"]["/custom-path"]


def test_generate_spec_with_pydantic_models():
    class RequestModel(BaseModel):
        username: str
        password: str

    class ResponseModel(BaseModel):
        message: str

    @openapi(
        summary="Login user",
        description="Authenticates a user and returns a welcome message.",
        request_model=RequestModel,
        response_model=ResponseModel,
        method="post",
        route="/login",
    )
    def login():
        pass

    spec = generate_openapi_spec()

    path = "/login"
    assert path in spec["paths"]
    assert "post" in spec["paths"][path]
    op = spec["paths"][path]["post"]

    assert (
        op["requestBody"]["content"]["application/json"]["schema"]["type"] == "object"
    )
    assert (
        "username"
        in op["requestBody"]["content"]["application/json"]["schema"]["properties"]
    )
    assert (
        "message"
        in op["responses"]["200"]["content"]["application/json"]["schema"]["properties"]
    )


def test_openapi_spec_contains_operation_id_and_tags():
    spec = json.loads(get_openapi_json())
    path_item = spec["paths"]["/http_trigger"]["get"]

    assert path_item["operationId"] == "greetUser"
    assert path_item["tags"] == ["Example"]
    assert path_item["summary"] == "HTTP Trigger with name parameter"
    assert (
        path_item["description"]
        == "Returns a greeting using the name from query or body."
    )
    assert "requestBody" in path_item
    assert "responses" in path_item
    assert "200" in path_item["responses"]
