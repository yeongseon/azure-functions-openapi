# tests/test_webhook_receiver_example.py
# (file kept as test_hello_openapi_function_app.py so CI mapping stays stable)

import importlib
import json
from typing import Any
from unittest.mock import patch

import azure.functions as func

import azure_functions_openapi.decorator as decorator_module
from examples.webhook_receiver import function_app


def _load_example_module() -> Any:
    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()
    return importlib.reload(function_app)


def test_receive_webhook_valid() -> None:
    fa = _load_example_module()
    payload = {
        "event_type": "order.completed",
        "source": "shopify",
        "occurred_at": "2026-04-12T00:00:00Z",
        "data": {"order_id": "12345"},
    }
    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=json.dumps(payload).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = fa.receive_order_webhook(req)

    assert resp.status_code == 202
    body = json.loads(resp.get_body())
    assert body["status"] == "accepted"
    assert "delivery_id" in body
    assert "received_at" in body


def test_receive_webhook_invalid_json() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=b"not json",
        params={},
        headers={},
    )

    resp = fa.receive_order_webhook(req)

    assert resp.status_code == 400
    assert "Invalid JSON" in json.loads(resp.get_body())["error"]


def test_receive_webhook_missing_required_fields() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=json.dumps({"data": {}}).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = fa.receive_order_webhook(req)

    assert resp.status_code == 400
    assert "required" in json.loads(resp.get_body())["error"]


def test_receive_webhook_non_object_body() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=json.dumps([1, 2, 3]).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )

    resp = fa.receive_order_webhook(req)

    assert resp.status_code == 400
    assert "JSON object" in json.loads(resp.get_body())["error"]


def test_receive_webhook_signature_valid() -> None:
    fa = _load_example_module()
    import hashlib
    import hmac

    payload = json.dumps({
        "event_type": "order.completed",
        "source": "shopify",
        "occurred_at": "2026-04-12T00:00:00Z",
        "data": {},
    }).encode("utf-8")
    secret = "test-secret"
    sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=payload,
        params={},
        headers={"Content-Type": "application/json", "X-Signature": sig},
    )

    with patch.dict("os.environ", {"WEBHOOK_SECRET": secret}):
        resp = fa.receive_order_webhook(req)

    assert resp.status_code == 202


def test_receive_webhook_signature_invalid() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(
        method="POST",
        url="/api/webhooks/orders",
        body=json.dumps({
            "event_type": "order.completed",
            "source": "shopify",
            "occurred_at": "2026-04-12T00:00:00Z",
            "data": {},
        }).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json", "X-Signature": "sha256=bad"},
    )

    with patch.dict("os.environ", {"WEBHOOK_SECRET": "test-secret"}):
        resp = fa.receive_order_webhook(req)

    assert resp.status_code == 401
    assert "signature" in json.loads(resp.get_body())["error"].lower()


def test_openapi_json_response() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(method="GET", url="/api/openapi.json", body=b"", params={}, headers={})
    resp = fa.openapi_spec(req)

    assert resp.status_code == 200
    payload = json.loads(resp.get_body())
    assert "paths" in payload
    assert "/receive_order_webhook" in payload["paths"]


def test_openapi_yaml_response() -> None:
    fa = _load_example_module()
    req = func.HttpRequest(method="GET", url="/api/openapi.yaml", body=b"", params={}, headers={})
    resp = fa.openapi_yaml_spec(req)

    assert resp.status_code == 200
    assert b"openapi:" in resp.get_body()
    assert b"paths:" in resp.get_body()
