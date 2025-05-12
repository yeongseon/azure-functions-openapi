# tests/test_openapi_spec.py
import json

from azure_functions_openapi.openapi import get_openapi_json


def test_openapi_spec_http_trigger_metadata() -> None:
    """Verify that the generated spec for /api/http_trigger contains the expected metadata."""
    spec = json.loads(get_openapi_json())

    # Ensure the path exists
    assert "/api/http_trigger" in spec["paths"]

    http_get = spec["paths"]["/api/http_trigger"]["get"]

    # Basic metadata
    assert http_get["operationId"] == "greetUser"
    assert http_get["tags"] == ["Example"]
    assert http_get["summary"] == "HTTP Trigger with name parameter"

    # Markdown description checks
    description = http_get["description"]
    assert "Returns a greeting using the **name**" in description
    assert "### Usage" in description
    assert "```json" in description

    # Response schema
    assert "responses" in http_get
    assert "200" in http_get["responses"]
