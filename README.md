# azure-functions-openapi

OpenAPI (Swagger) integration for Python-based Azure Functions.

## Overview

This library enables automatic generation of OpenAPI (Swagger) documentation for your Python Azure Functions.
It supports route/method inference, request/response schema generation via Pydantic, and built-in Swagger UI.

## Features

- `@openapi` decorator to register function metadata
- Auto-generation of `/openapi.json` and `/openapi.yaml`
- Built-in `/swagger` endpoint for Swagger UI
- Supports `parameters`, `requestBody`, `responses`, and `tags`
- Supports `pydantic` models for schema inference

## Installation

```bash
pip install azure-functions-openapi
```

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .
```

## Example

```python
from pydantic import BaseModel
from azure_functions_openapi.decorator import openapi

class RequestModel(BaseModel):
    name: str

class ResponseModel(BaseModel):
    message: str

@openapi(
    summary="Greet user",
    description="Returns a greeting using the name.\n\n### Usage\n`?name=Azure`\n\n```json\n{ \"name\": \"Azure\" }\n```",
    request_model=RequestModel,
    response_model=ResponseModel,
    tags=["Example"],
    operation_id="greetUser"
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

Visit:
- [http://localhost:7071/swagger](http://localhost:7071/swagger) for Swagger UI
- [http://localhost:7071/openapi.json](http://localhost:7071/openapi.json) for OpenAPI spec

## Development

See [docs/development.md](docs/development.md) for environment setup, testing, linting, and pre-commit configuration.

## Contributing

Contributions are welcome! See [docs/contributing.md](docs/contributing.md) for guidelines.

## License

MIT © Yeongseon Choe
