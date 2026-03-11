import importlib
import json
from typing import Any

import azure.functions as func
import pytest

try:
    import azure_functions_openapi.decorator as decorator_module
    from examples.with_validation import function_app as validation_function_app
    HAS_VALIDATION = True
except ImportError:
    HAS_VALIDATION = False

pytestmark = pytest.mark.skipif(
    not HAS_VALIDATION,
    reason="azure-functions-validation not installed",
)

def _load_example_module() -> Any:
    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()
    return importlib.reload(validation_function_app)


def test_create_user_valid() -> None:
    function_app = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/users",
        body=json.dumps({"name": "Alice", "email": "alice@example.com"}).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = function_app.create_user(req)

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"
    assert body["id"] == 1


def test_create_user_invalid_body() -> None:
    function_app = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/users",
        body=b'{"name": "Alice"}',  # missing email
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = function_app.create_user(req)

    assert resp.status_code == 422
    body = json.loads(resp.get_body())
    assert "detail" in body


def test_create_user_no_body() -> None:
    function_app = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/users",
        body=b"",
        params={},
        headers={},
    )

    resp = function_app.create_user(req)

    assert resp.status_code in (400, 422)


def test_get_user_found() -> None:
    function_app = _load_example_module()
    function_app.USERS.append({"id": 1, "name": "Bob", "email": "bob@example.com"})

    req = func.HttpRequest(
        method="GET",
        url="/api/users/1",
        body=b"",
        route_params={"user_id": "1"},
        params={},
        headers={},
    )

    resp = function_app.get_user(req)

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["name"] == "Bob"
    assert body["id"] == 1


def test_get_user_not_found() -> None:
    function_app = _load_example_module()

    req = func.HttpRequest(
        method="GET",
        url="/api/users/999",
        body=b"",
        route_params={"user_id": "999"},
        params={},
        headers={},
    )

    resp = function_app.get_user(req)

    assert resp.status_code == 404


def test_openapi_spec_includes_user_paths() -> None:
    function_app = _load_example_module()

    req = func.HttpRequest(
        method="GET",
        url="/api/openapi.json",
        body=b"",
        params={},
        headers={},
    )

    resp = function_app.openapi_spec(req)

    assert resp.status_code == 200
    payload = json.loads(resp.get_body())
    assert any("/api/users" in p for p in payload["paths"]), payload["paths"].keys()
