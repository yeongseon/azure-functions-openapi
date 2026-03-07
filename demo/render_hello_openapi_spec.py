from __future__ import annotations

from importlib import import_module, reload
from pathlib import Path
import sys

import azure_functions_openapi.decorator as decorator_module
from azure_functions_openapi.openapi import get_openapi_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()

    module = import_module("examples.hello_openapi.function_app")
    reload(module)

    print(
        get_openapi_yaml(
            title="Hello OpenAPI Demo",
            version="1.0.0",
        )
    )


if __name__ == "__main__":
    main()
