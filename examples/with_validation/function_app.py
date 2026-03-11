
import logging
from typing import Any, Dict, List

import azure.functions as func
from pydantic import BaseModel, Field

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui
from azure_functions_validation import validate_http

app = func.FunctionApp()


class CreateUserRequest(BaseModel):
    name: str
    email: str


class UserQuery(BaseModel):
    include_profile: bool = Field(default=False)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


USERS: List[Dict[str, Any]] = []


@app.function_name(name="create_user")
@app.route(route="users", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Create a new user",
    description="Create a user with name and email.",
    tags=["Users"],
    operation_id="createUser",
    route="/api/users",
    method="post",
    request_model=CreateUserRequest,
    response_model=UserResponse,
    response={
        201: {"description": "User created"},
        422: {"description": "Validation error"},
    },
)
@validate_http(body=CreateUserRequest, response_model=UserResponse)
def create_user(req: func.HttpRequest, body: CreateUserRequest) -> UserResponse:
    """
    Create a new user.

    Parameters:
        req: The HTTP request object.
        body: The validated request payload.
    Returns:
        The created user.
    """
    logging.info("Creating a new user")
    user = {"id": len(USERS) + 1, "name": body.name, "email": body.email}
    USERS.append(user)
    return UserResponse(**user)


@app.function_name(name="get_user")
@app.route(route="users/{user_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    summary="Get a user by ID",
    description="Retrieve a user by id with validated query options.",
    tags=["Users"],
    operation_id="getUser",
    route="/api/users/{user_id}",
    method="get",
    parameters=[
        {
            "name": "user_id",
            "in": "path",
            "required": True,
            "description": "The ID of the user to retrieve.",
            "schema": {"type": "integer"},
        },
        {
            "name": "include_profile",
            "in": "query",
            "required": False,
            "description": "Include profile metadata in lookup behavior.",
            "schema": {"type": "boolean", "default": False},
        },
    ],
    response_model=UserResponse,
    response={
        200: {"description": "User found"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
    },
)
@validate_http(query=UserQuery, response_model=UserResponse)
def get_user(req: func.HttpRequest, query: UserQuery):
    """
    Get a user by ID.

    Parameters:
        req: The HTTP request object.
        query: The validated query parameters.
    Returns:
        The requested user, or not found response.
    """
    logging.info("Getting a user by ID")
    user_id = int(req.route_params.get("user_id", "0"))
    user = next((item for item in USERS if item["id"] == user_id), None)

    if user is None:
        return func.HttpResponse("User not found", status_code=404)

    if query.include_profile:
        logging.info("include_profile query option enabled")

    return UserResponse(**user)


@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_spec")
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate OpenAPI specification in JSON format.

    Parameters:
        req: The HTTP request object.
    Returns:
        A JSON response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI spec")
    return func.HttpResponse(get_openapi_json(), mimetype="application/json", status_code=200)


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="openapi_yaml_spec")
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    """
    Generate OpenAPI specification in YAML format.

    Parameters:
        req: The HTTP request object.
    Returns:
        A YAML response containing the OpenAPI specification.
    """
    logging.info("Generating OpenAPI YAML spec")
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml", status_code=200)


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    """
    Serve Swagger UI for OpenAPI documentation.

    Parameters:
        req: The HTTP request object.
    Returns:
        A response containing the Swagger UI.
    """
    logging.info("Serving Swagger UI")
    return render_swagger_ui()
