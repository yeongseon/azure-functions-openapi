# tests/test_openapi.py

from azure_functions_openapi.openapi import generate_openapi_spec, get_openapi_json
from azure_functions_openapi.decorator import openapi, get_openapi_registry
import json


def test_generate_openapi_spec_structure():
    @openapi(
        summary="Sample summary",
        description="Sample description",
        response={200: {"description": "Success"}},
    )
    def sample_func():
        pass

    # Ensure the function is registered
    registry = get_openapi_registry()
    assert "sample_func" in registry

    # Generate OpenAPI spec
    spec = generate_openapi_spec(title="My API", version="1.2.3")

    assert spec["openapi"] == "3.0.0"
    assert spec["info"]["title"] == "My API"
    assert spec["info"]["version"] == "1.2.3"
    assert "/sample_func" in spec["paths"]
    assert "get" in spec["paths"]["/sample_func"]
    assert spec["paths"]["/sample_func"]["get"]["summary"] == "Sample summary"


def test_get_openapi_json_output():
    json_str = get_openapi_json()
    data = json.loads(json_str)

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    assert isinstance(data["paths"], dict)
