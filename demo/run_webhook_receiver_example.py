from __future__ import annotations

import argparse
from html import escape
from importlib import import_module, reload
from pathlib import Path
import sys

import yaml

from azure_functions_openapi import get_openapi_json, get_openapi_yaml
import azure_functions_openapi.decorator as decorator_module
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


def _build_spec_preview_html(openapi_yaml: str) -> str:
    highlighted_yaml = escape(openapi_yaml.strip())
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Webhook Receiver OpenAPI Spec Preview</title>
    <style>
      :root {{
        color-scheme: dark;
      }}
      body {{
        margin: 0;
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #e5e7eb;
        font-family: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
      }}
      main {{
        padding: 40px;
      }}
      .panel {{
        max-width: 1120px;
        margin: 0 auto;
        background: rgba(15, 23, 42, 0.94);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 18px;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.45);
        overflow: hidden;
      }}
      .panel-header {{
        padding: 18px 24px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(30, 41, 59, 0.85);
      }}
      .eyebrow {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 13px;
        color: #bfdbfe;
        background: rgba(37, 99, 235, 0.22);
      }}
      h1 {{
        margin: 14px 0 8px;
        font-size: 32px;
        font-weight: 700;
      }}
      p {{
        margin: 0;
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.5;
      }}
      pre {{
        margin: 0;
        padding: 28px 32px 36px;
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
        color: #e2e8f0;
      }}
      .comment {{
        color: #94a3b8;
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="panel">
        <div class="panel-header">
          <span class="eyebrow">Generated from examples/webhook_receiver</span>
          <h1>OpenAPI Output</h1>
          <p>
            The representative example produces this OpenAPI document before
            Swagger UI renders it.
          </p>
        </div>
        <pre>{highlighted_yaml}</pre>
      </section>
    </main>
  </body>
</html>
"""


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
        description="Run the representative webhook_receiver example and generate demo assets."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    swagger_dir = output_dir / "swagger-ui"
    spec_dir = output_dir / "spec-preview"
    swagger_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    with decorator_module._registry_lock:
        decorator_module._openapi_registry.clear()

    module = import_module("examples.webhook_receiver.function_app")
    reload(module)

    openapi_yaml = get_openapi_yaml(
        title="Webhook Receiver OpenAPI Demo",
        version="1.0.0",
    )
    openapi_json = get_openapi_json(
        title="Webhook Receiver OpenAPI Demo",
        version="1.0.0",
    )
    swagger_response = render_swagger_ui(
        title="Webhook Receiver OpenAPI Demo",
        openapi_url="/openapi.json",
    )

    (output_dir / "openapi.yaml").write_text(openapi_yaml, encoding="utf-8")
    (output_dir / "openapi.json").write_text(openapi_json, encoding="utf-8")
    (spec_dir / "index.html").write_text(
        _build_spec_preview_html(openapi_yaml),
        encoding="utf-8",
    )
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

    print("Representative example: examples/webhook_receiver/function_app.py")
    print(f"Generated: {output_dir / 'openapi.yaml'}")
    print(f"Generated: {spec_dir / 'index.html'}")
    print(f"Generated: {swagger_dir / 'index.html'}")
    print()
    print(preview)


if __name__ == "__main__":
    main()
