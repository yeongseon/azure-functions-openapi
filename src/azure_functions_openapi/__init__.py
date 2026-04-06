# src/azure_functions_openapi/__init__.py

from azure_functions_openapi.decorator import (
    clear_openapi_registry,
    openapi,
    register_openapi_metadata,
)
from azure_functions_openapi.exceptions import OpenAPISpecConfigError
from azure_functions_openapi.openapi import (
    OPENAPI_VERSION_3_0,
    OPENAPI_VERSION_3_1,
    generate_openapi_spec,
    get_openapi_json,
    get_openapi_yaml,
)
from azure_functions_openapi.swagger_ui import render_swagger_ui
from azure_functions_openapi.types import OpenAPIOperationMetadata

__version__ = "0.16.0"

__all__ = [
    "__version__",
    "OPENAPI_VERSION_3_0",
    "OPENAPI_VERSION_3_1",
    "OpenAPISpecConfigError",
    "OpenAPIOperationMetadata",
    "clear_openapi_registry",
    "generate_openapi_spec",
    "get_openapi_json",
    "get_openapi_yaml",
    "openapi",
    "register_openapi_metadata",
    "render_swagger_ui",
]
