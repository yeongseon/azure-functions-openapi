# src/azure_functions_openapi/__init__.py
import azure_functions_openapi.bridge as _bridge
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

# The `.decorator` import MUST stay last. Importing the `.openapi` submodule
# above sets it as the `openapi` attribute on this package; importing the
# decorator named `openapi` last rebinds that attribute to the callable so
# `from azure_functions_openapi import openapi` resolves to the decorator,
# matching `__all__` and `docs/api.md`.
from azure_functions_openapi.decorator import (
    clear_openapi_registry,
    openapi,
    register_openapi_metadata,
)

__version__ = "0.17.1"
scan_validation_metadata = _bridge.scan_validation_metadata

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
    "scan_validation_metadata",
]
