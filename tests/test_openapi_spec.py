import json
from azure_functions_openapi.openapi import get_openapi_json


def test_openapi_spec_http_trigger_metadata():
    spec = json.loads(get_openapi_json())

    assert "/http_trigger" in spec["paths"]
    http_get = spec["paths"]["/http_trigger"]["get"]

    # Check metadata fields
    assert http_get["operationId"] == "greetUser"
    assert http_get["tags"] == ["Example"]
    assert http_get["summary"] == "HTTP Trigger with name parameter"
    assert (
        http_get["description"]
        == "Returns a greeting using the name from query or body."
    )

    # Check requestBody schema presence
    assert "requestBody" in http_get
    assert "application/json" in http_get["requestBody"]["content"]
    assert "schema" in http_get["requestBody"]["content"]["application/json"]

    # Check responses
    assert "responses" in http_get
    assert "200" in http_get["responses"]
    assert http_get["responses"]["200"]["description"] == "Successful Response"
