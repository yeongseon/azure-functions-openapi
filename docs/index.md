# Azure Functions OpenAPI

`azure-functions-openapi` adds OpenAPI (Swagger) documentation to **Azure Functions Python v2** applications.
It generates OpenAPI 3.0 and 3.1 specifications from decorator metadata attached to HTTP-triggered functions
and serves an interactive Swagger UI at runtime.

## Key Features

- **Decorator-based metadata** -- `@openapi` attaches summary, parameters, request/response schemas, security requirements, and tags to each endpoint.
- **Automatic spec generation** -- `get_openapi_json()` and `get_openapi_yaml()` compile all registered metadata into a complete OpenAPI document.
- **Swagger UI** -- `render_swagger_ui()` serves an interactive documentation page with built-in Content Security Policy headers.
- **Pydantic integration** -- Request and response schemas are derived automatically from Pydantic v1 and v2 `BaseModel` classes.
- **Security schemes** -- Supports `apiKey`, `http`, `oauth2`, and `openIdConnect` scheme types with per-decorator or centralized definitions.
- **OpenAPI 3.0 and 3.1** -- Choose the specification version at generation time; nullable types and example formats are converted automatically.
- **CLI tooling** -- `azure-functions-openapi generate` produces spec files for offline validation and CI pipelines.

## Compatibility

| Requirement | Version |
| --- | --- |
| Python | 3.10 -- 3.14 |
| Azure Functions model | v2 (`func.FunctionApp` with decorators) |
| Pydantic | 1.10+ and 2.x |
| OpenAPI output | 3.0.0 and 3.1.0 |

This library is **not** compatible with the legacy `function.json`-based v1 programming model.

## Quick Start

Install the package:

```bash
pip install azure-functions-openapi
```

Decorate your HTTP functions:

```python
import azure.functions as func
from azure_functions_openapi import openapi, get_openapi_json, render_swagger_ui

app = func.FunctionApp()


@app.function_name(name="hello")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
@openapi(summary="Hello endpoint", route="/api/hello", tags=["Example"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, world!", status_code=200)


@app.function_name(name="openapi_spec")
@app.route(route="openapi.json", methods=["GET"])
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    body = get_openapi_json(title="My API", version="1.0.0")
    return func.HttpResponse(body, mimetype="application/json")


@app.function_name(name="swagger_ui")
@app.route(route="docs", methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

Start the function app:

```bash
func start
```

Then open `http://localhost:7071/api/docs` to see the Swagger UI, or fetch
`http://localhost:7071/api/openapi.json` for the raw specification.

## Project Layout

```text
azure-functions-openapi/
  src/azure_functions_openapi/
    __init__.py        # Public API exports
    decorator.py       # @openapi decorator and registry
    openapi.py         # Spec generation (JSON, YAML)
    swagger_ui.py      # Swagger UI renderer
    cli.py             # CLI entry point
    utils.py           # Schema conversion and validation
  tests/               # Unit and integration tests
  examples/            # Sample Azure Functions projects
  docs/                # MkDocs documentation
```

## Examples

The `examples/` directory contains complete Azure Functions projects:

- **hello** -- Minimal single-endpoint project demonstrating the decorator and spec routes.
- **todo_crud** -- Multi-endpoint CRUD API with Pydantic models, path parameters, and custom responses.
- **with_validation** -- Integration with `azure-functions-validation` for runtime request validation.

Each example includes a `function_app.py`, `requirements.txt`, and `host.json` and can be started
directly with `func start`.

## Documentation

| Page | Description |
| --- | --- |
| [Installation](installation.md) | Requirements, install commands, and deployment setup |
| [Usage Guide](usage.md) | Decorator parameters, Pydantic models, security schemes, output routes |
| [API Reference](api.md) | Full API signatures and parameter documentation |
| [CLI](cli.md) | Command-line spec generation |
| [Architecture](architecture.md) | Internal design, registry, and spec compilation flow |
| [Development](development.md) | Local setup, Makefile targets, pre-commit hooks |
| [Testing](testing.md) | Test structure, coverage policy, adding new tests |
| [Troubleshooting](troubleshooting.md) | Common errors and solutions |
| [Security](security.md) | Security model, CSP headers, vulnerability reporting |
| [Release Process](release_process.md) | Versioning, tagging, and PyPI publishing |
| [Changelog](changelog.md) | Version history |
| [Contributing](contributing.md) | Contribution workflow, commit conventions, code of conduct |

## License

MIT License. See [LICENSE](https://github.com/yeongseon/azure-functions-openapi/blob/main/LICENSE).
