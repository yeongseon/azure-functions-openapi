import json
import importlib
from typing import Any

import azure.functions as func
from pydantic import BaseModel

from azure_functions_openapi import scan_validation_metadata
from azure_functions_openapi.openapi import get_openapi_json
from azure_functions_openapi.swagger_ui import render_swagger_ui

validate_http = getattr(importlib.import_module("azure_functions_validation"), "validate_http")

app = func.FunctionApp()


class CreateItemBody(BaseModel):
    name: str


class ItemPath(BaseModel):
    item_id: int


class ItemResponse(BaseModel):
    id: int
    name: str


ITEMS: list[dict[str, Any]] = []


@app.function_name(name="create_item")
@app.route(route="items", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@validate_http(body=CreateItemBody, response_model=ItemResponse)
def create_item(req: func.HttpRequest, body: CreateItemBody) -> ItemResponse:
    item_id = len(ITEMS) + 1
    item = {"id": item_id, "name": body.name}
    ITEMS.append(item)
    return ItemResponse(id=item_id, name=body.name)


@app.function_name(name="get_item")
@app.route(route="items/{item_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@validate_http(path=ItemPath, response_model=ItemResponse)
def get_item(req: func.HttpRequest, path: ItemPath) -> func.HttpResponse:
    item = next((entry for entry in ITEMS if entry["id"] == path.item_id), None)
    if item is None:
        return func.HttpResponse("Not found", status_code=404)
    return func.HttpResponse(json.dumps(item), mimetype="application/json", status_code=200)


scan_validation_metadata(app)


@app.function_name(name="openapi_spec")
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(title="Bridge Example"), mimetype="application/json")


@app.function_name(name="swagger_ui")
@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
