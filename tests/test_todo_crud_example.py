import importlib
import json
from typing import Any

import azure.functions as func

import azure_functions_openapi.decorator as decorator_module
from examples.todo_crud_api import function_app as todo_function_app


def _load_example_module() -> Any:
    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()
    return importlib.reload(todo_function_app)


def test_todo_crud_example_create_and_list() -> None:
    function_app = _load_example_module()
    create_request = func.HttpRequest(
        method="POST",
        url="/api/create_todo",
        body=json.dumps({"title": "Ship examples"}).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )

    create_response = function_app.create_todo(create_request)

    assert create_response.status_code == 201
    assert json.loads(create_response.get_body()) == {
        "id": 1,
        "title": "Ship examples",
        "done": False,
    }

    list_request = func.HttpRequest(
        method="GET",
        url="/api/list_todos",
        body=b"",
        params={},
        headers={},
    )
    list_response = function_app.list_todos(list_request)

    assert list_response.status_code == 200
    assert json.loads(list_response.get_body()) == {
        "todos": [{"id": 1, "title": "Ship examples", "done": False}]
    }


def test_todo_crud_example_update_delete_and_spec() -> None:
    function_app = _load_example_module()
    function_app.TODOS.append({"id": 1, "title": "Ship examples", "done": False})

    update_request = func.HttpRequest(
        method="PUT",
        url="/api/update_todo",
        body=json.dumps({"id": 1, "title": "Ship examples now", "done": True}).encode("utf-8"),
        params={},
        headers={"Content-Type": "application/json"},
    )
    update_response = function_app.update_todo(update_request)

    assert update_response.status_code == 200
    assert json.loads(update_response.get_body()) == {
        "id": 1,
        "title": "Ship examples now",
        "done": True,
    }

    spec_request = func.HttpRequest(
        method="GET",
        url="/api/openapi.json",
        body=b"",
        params={},
        headers={},
    )
    spec_response = function_app.openapi_spec(spec_request)

    assert spec_response.status_code == 200
    payload = json.loads(spec_response.get_body())
    assert "/api/create_todo" in payload["paths"]

    delete_request = func.HttpRequest(
        method="DELETE",
        url="/api/delete_todo?id=1",
        body=b"",
        params={"id": "1"},
        headers={},
    )
    delete_response = function_app.delete_todo(delete_request)

    assert delete_response.status_code == 204
    assert function_app.TODOS == []
