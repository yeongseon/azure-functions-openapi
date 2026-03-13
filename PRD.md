# PRD - azure-functions-openapi

## Overview

`azure-functions-openapi` provides OpenAPI document generation and Swagger UI support for the
Azure Functions Python v2 programming model.

It is intended for decorator-based `func.FunctionApp()` applications that want lightweight API
documentation without adopting a full web framework.

## Problem Statement

Azure Functions Python applications often expose HTTP APIs without a consistent way to:

- define endpoint documentation close to handler code
- generate OpenAPI documents from that metadata
- render Swagger UI for local or hosted inspection

This leads to duplicated documentation, drift between implementation and docs, and inconsistent
developer experience across projects.

## Goals

- Provide a small decorator-first API for endpoint metadata.
- Generate OpenAPI JSON and YAML from registered handlers.
- Render Swagger UI from generated specifications.
- Stay aligned with Azure Functions Python v2 and companion libraries in this ecosystem.

## Non-Goals

- Building a full routing framework
- Replacing Azure Functions runtime concepts
- Owning request validation or response validation at runtime
- Supporting the legacy `function.json`-based Python v1 model

## Primary Users

- Maintainers of Azure Functions Python HTTP APIs
- Teams that want OpenAPI output without leaving the Azure Functions model
- Users pairing this package with `azure-functions-validation`

## Core Use Cases

- Annotate a handler with OpenAPI metadata
- Generate `/openapi.json` and `/openapi.yaml`
- Serve Swagger UI for the same application
- Produce spec artifacts via CLI or automation

## Success Criteria

- Supported examples generate valid OpenAPI output in CI
- Representative examples render correctly in Swagger UI
- Documentation and generated output stay aligned through smoke tests

## Example-First Design

### Philosophy

Small-ecosystem libraries succeed when developers can copy a working example and see
results immediately. `azure-functions-openapi` treats runnable examples as a first-class
deliverable — every decorator feature should have a corresponding example that produces
a real OpenAPI document and renders in Swagger UI.

### Quick Start (Hello World)

The shortest path from zero to a documented endpoint:

```python
import json

import azure.functions as func

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json
from azure_functions_openapi.swagger_ui import render_swagger_ui


app = func.FunctionApp()


@app.function_name(name="hello")
@app.route(route="hello", methods=["GET"])
@openapi(summary="Say hello", route="/api/hello", method="get")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps({"message": "Hello!"}), mimetype="application/json")


@app.function_name(name="openapi_json")
@app.route(route="openapi.json", methods=["GET"])
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_json(title="My API")


@app.function_name(name="docs")
@app.route(route="docs", methods=["GET"])
def docs(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

Run `func start`, then open `http://localhost:7071/api/docs` for Swagger UI.

### Why Examples Matter

1. **Lower entry barrier.** A working Hello World in the PRD and README lets developers
   evaluate the library before reading any reference documentation.
2. **AI agent discoverability.** Tools like GitHub Copilot, Cursor, and Claude Code recommend
   libraries based on README, PRD, and example content. Rich examples increase the chance
   that AI agents surface `azure-functions-openapi` for relevant prompts.
3. **Cookbook role.** For niche ecosystems, `examples/` and `docs/` often serve as the primary
   learning material. Every new pattern should ship with a runnable example project.
4. **Proven approach.** FastAPI, LangChain, SQLAlchemy, and Pandas all achieved early adoption
   through extensive, copy-paste-friendly examples.

### Examples Inventory

| Role | Path | Pattern |
|---|---|---|
| Representative | `examples/hello` | Minimal HTTP trigger with OpenAPI and Swagger UI |
| Representative | `examples/hello_openapi` | Extended OpenAPI metadata example |
| Complex | `examples/todo_crud` | CRUD app with Pydantic models and generated spec |
| Complex | `examples/todo_crud_api` | Full CRUD API with validation integration |
| Integration | `examples/with_validation` | Combined `@openapi` and `@validate_http` |

All examples are smoke-tested in CI. New features must ship with a corresponding example
or an extension to an existing one.
