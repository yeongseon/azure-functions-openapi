# tests/test_decorator.py

from azure_functions_openapi.decorator import openapi, get_openapi_registry


def test_openapi_registers_metadata():
    @openapi(
        summary="Test Summary",
        description="Detailed test description",
        response={200: {"description": "OK"}},
    )
    def dummy_function():
        pass

    registry = get_openapi_registry()
    assert "dummy_function" in registry
    assert registry["dummy_function"]["summary"] == "Test Summary"
    assert registry["dummy_function"]["description"] == "Detailed test description"
    assert 200 in registry["dummy_function"]["response"]
