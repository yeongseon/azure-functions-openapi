from __future__ import annotations

import argparse
from importlib import import_module, reload
from pathlib import Path
import sys

import yaml

import azure_functions_openapi.decorator as decorator_module
from azure_functions_openapi.openapi import get_openapi_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()

    module = import_module("examples.hello_openapi.function_app")
    reload(module)

    openapi_yaml = get_openapi_yaml(
        title="Hello OpenAPI Demo",
        version="1.0.0",
    )
    if args.output is not None:
        args.output.write_text(openapi_yaml, encoding="utf-8")

    print(
        yaml.safe_dump(
            _build_preview(yaml.safe_load(openapi_yaml)),
            sort_keys=False,
            default_flow_style=False,
        ).strip()
    )


if __name__ == "__main__":
    main()
