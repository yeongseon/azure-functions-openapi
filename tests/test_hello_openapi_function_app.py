# tests/test_hello_openapi_function_app.py

import azure.functions as func

from examples.hello_openapi import function_app


def test_http_trigger_query() -> None:
    req = func.HttpRequest(
        method="GET",
        url="/api/http_trigger?name=Azure",
        body=b"",
        params={"name": "Azure"},
        headers={},
    )

    resp = function_app.http_trigger(req)
    assert resp.status_code == 200
    assert "Hello, Azure" in resp.get_body().decode()


def test_http_trigger_body() -> None:
    req = func.HttpRequest(
        method="POST",
        url="/api/http_trigger",
        body=b'{"name": "Function"}',
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = function_app.http_trigger(req)
    assert resp.status_code == 200
    assert "Hello, Function" in resp.get_body().decode()


def test_http_trigger_no_name() -> None:
    req = func.HttpRequest(method="GET", url="/api/http_trigger", body=b"", params={}, headers={})

    resp = function_app.http_trigger(req)
    assert resp.status_code == 400
    assert "Invalid request" in resp.get_body().decode()


def test_openapi_yaml_response() -> None:
    req = func.HttpRequest(method="GET", url="/api/openapi.yaml", body=b"", params={}, headers={})
    resp = function_app.openapi_yaml_spec(req)

    assert resp.status_code == 200
    assert b"openapi:" in resp.get_body()
    assert b"paths:" in resp.get_body()
