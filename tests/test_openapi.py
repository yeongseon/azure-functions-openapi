# tests/test_openapi.py
import json

from pydantic import BaseModel

from azure_functions_openapi.decorator import get_openapi_registry, openapi
from azure_functions_openapi.openapi import generate_openapi_spec, get_openapi_json


def test_generate_openapi_spec_structure() -> None:
    @openapi(
        route="/sample_func",
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
    )
    def sample_func() -> None:
        pass

    spec = generate_openapi_spec(title="My API", version="1.2.3")

    assert spec["openapi"] == "3.0.0"
    assert spec["info"]["title"] == "My API"
    assert spec["info"]["version"] == "1.2.3"
    assert "/sample_func" in spec["paths"]

    op = spec["paths"]["/sample_func"]["get"]
    p = op["parameters"][0]
    assert p == {
        "name": "q",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
        "description": "Optional query string",
    }


def test_get_openapi_json_output() -> None:
    data = json.loads(get_openapi_json())

    assert {"openapi", "info", "paths"} <= data.keys()
    assert isinstance(data["paths"], dict)


def test_generate_openapi_spec_with_request_body() -> None:
    @openapi(
        route="/func_with_body",
        method="post",
        summary="With Body",
        description="Endpoint with request body",
        response={200: {"description": "OK"}},
    )
    def func_with_body() -> None:
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
    rb = spec["paths"]["/func_with_body"]["post"]["requestBody"]
    schema = rb["content"]["application/json"]["schema"]
    assert {"username", "password"} <= schema["properties"].keys()


def test_response_schema_and_examples() -> None:
    @openapi(
        route="/greet",
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
    )
    def greet() -> None:
        pass

    op = generate_openapi_spec()["paths"]["/greet"]["get"]
    assert (
        op["responses"]["200"]["content"]["application/json"]["examples"]["sample"]["value"][
            "message"
        ]
        == "Hello, Azure!"
    )


def test_generate_openapi_spec_with_route_and_method() -> None:
    @openapi(
        route="/custom-path",
        summary="Test with custom route/method",
        description="Checks that route and method are reflected",
        response={200: {"description": "OK"}},
        method="post",
    )
    def custom_func() -> None:
        pass

    spec = generate_openapi_spec()
    assert "post" in spec["paths"]["/custom-path"]


def test_generate_spec_with_pydantic_models() -> None:
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
    )
    def login() -> None:
        pass

    op = generate_openapi_spec()["paths"]["/login"]["post"]
    schema_req = op["requestBody"]["content"]["application/json"]["schema"]
    schema_resp = op["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema_req == {"$ref": "#/components/schemas/RequestModel"}
    assert schema_resp == {"$ref": "#/components/schemas/ResponseModel"}

    spec = generate_openapi_spec()
    components = spec.get("components", {})
    schemas = components.get("schemas", {})
    assert "RequestModel" in schemas
    assert "ResponseModel" in schemas
    assert "$defs" not in schemas["RequestModel"]
    assert "$defs" not in schemas["ResponseModel"]


def test_openapi_spec_contains_operation_id_and_tags() -> None:
    spec = json.loads(get_openapi_json())
    item = spec["paths"]["/api/http_trigger"]["get"]

    assert item["operationId"] == "greetUser"
    assert item["tags"] == ["Example"]
    assert "HTTP Trigger with name parameter" in item["summary"]
    assert "### Usage" in item["description"]
    # GET operations have no requestBody
    assert "responses" in item and "200" in item["responses"]


def test_markdown_description_rendering() -> None:
    item = json.loads(get_openapi_json())["paths"]["/api/http_trigger"]["get"]
    desc = item["description"]
    assert "### Usage" in desc and "`?name=Azure`" in desc and "```json" in desc


def test_generate_openapi_spec_with_cookie_parameter() -> None:
    @openapi(
        route="/cookie_test",
        summary="Cookie param example",
        description="Test endpoint with cookie parameter",
        parameters=[
            {
                "name": "session_id",
                "in": "cookie",
                "required": True,
                "schema": {"type": "string"},
                "description": "User session ID",
            }
        ],
    )
    def cookie_test() -> None:
        pass

    params = generate_openapi_spec()["paths"]["/cookie_test"]["get"]["parameters"]
    cookie_param = next(p for p in params if p["in"] == "cookie")
    assert cookie_param["name"] == "session_id"
