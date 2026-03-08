from __future__ import annotations

import argparse
from importlib import import_module, reload
from pathlib import Path
import sys

import yaml

import azure_functions_openapi.decorator as decorator_module
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _expand_swagger_ui(html: str) -> str:
    expanded_layout = (
        "layout: 'BaseLayout',\n"
        "            docExpansion: 'full',\n"
        "            defaultModelsExpandDepth: -1,\n"
        "            tryItOutEnabled: false,\n"
        "            supportedSubmitMethods: [],"
    )
    return html.replace(
        "layout: 'BaseLayout',",
        expanded_layout,
    )


def _build_preview(spec: dict[str, object]) -> dict[str, object]:
    paths = spec.get("paths", {})
    if not isinstance(paths, dict) or not paths:
        raise RuntimeError("Generated OpenAPI document does not contain any paths")

    path_name, operations = next(iter(paths.items()))
    if not isinstance(operations, dict) or not operations:
        raise RuntimeError("Generated OpenAPI document does not contain any operations")

    method_name, operation = next(iter(operations.items()))
    if not isinstance(operation, dict):
        raise RuntimeError("Generated OpenAPI operation is invalid")

    responses = operation.get("responses", {})
    preview_responses: dict[str, str] = {}
    if isinstance(responses, dict):
        for code, value in responses.items():
            if isinstance(value, dict):
                preview_responses[str(code)] = str(value.get("description", ""))

    return {
        "openapi": spec.get("openapi"),
        "info": {
            "title": (
                spec.get("info", {}).get("title") if isinstance(spec.get("info"), dict) else None
            ),
            "version": (
                spec.get("info", {}).get("version") if isinstance(spec.get("info"), dict) else None
            ),
        },
        "paths": {
            str(path_name): {
                str(method_name): {
                    "summary": operation.get("summary"),
                    "operationId": operation.get("operationId"),
                    "responses": preview_responses,
                }
            }
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the representative hello_openapi example and generate demo assets."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    swagger_dir = output_dir / "swagger-ui"
    swagger_dir.mkdir(parents=True, exist_ok=True)

    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()

    module = import_module("examples.hello_openapi.function_app")
    reload(module)

    openapi_yaml = get_openapi_yaml(
        title="Hello OpenAPI Demo",
        version="1.0.0",
    )
    openapi_json = get_openapi_json(
        title="Hello OpenAPI Demo",
        version="1.0.0",
    )
    swagger_response = render_swagger_ui(
        title="Hello OpenAPI Demo",
        openapi_url="/openapi.json",
    )

    (output_dir / "openapi.yaml").write_text(openapi_yaml, encoding="utf-8")
    (output_dir / "openapi.json").write_text(openapi_json, encoding="utf-8")
    (swagger_dir / "openapi.json").write_text(openapi_json, encoding="utf-8")
    (swagger_dir / "index.html").write_text(
        _expand_swagger_ui(swagger_response.get_body().decode("utf-8")),
        encoding="utf-8",
    )

    spec = yaml.safe_load(openapi_yaml)
    preview = yaml.safe_dump(
        _build_preview(spec),
        sort_keys=False,
        default_flow_style=False,
    ).strip()

    print("Representative example: examples/hello_openapi/function_app.py")
    print(f"Generated: {output_dir / 'openapi.yaml'}")
    print(f"Generated: {swagger_dir / 'index.html'}")
    print()
    print(preview)


if __name__ == "__main__":
    main()
