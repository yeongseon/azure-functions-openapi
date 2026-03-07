from __future__ import annotations

import argparse
from importlib import import_module, reload
from pathlib import Path
import sys

import azure_functions_openapi.decorator as decorator_module
from azure_functions_openapi.openapi import get_openapi_json
from azure_functions_openapi.swagger_ui import render_swagger_ui

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()

    module = import_module("examples.hello_openapi.function_app")
    reload(module)

    openapi_json = get_openapi_json(
        title="Hello OpenAPI Demo",
        version="1.0.0",
    )
    swagger_response = render_swagger_ui(
        title="Hello OpenAPI Demo",
        openapi_url="/openapi.json",
    )

    (output_dir / "openapi.json").write_text(openapi_json, encoding="utf-8")
    (output_dir / "index.html").write_bytes(swagger_response.get_body())


if __name__ == "__main__":
    main()
