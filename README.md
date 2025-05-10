# azure-functions-openapi

[![PyPI](https://img.shields.io/pypi/v/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![Python Version](https://img.shields.io/pypi/pyversions/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![CI](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-openapi/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-openapi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-openapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Effortless OpenAPI ( Swagger ) documentation & Swagger‑UI for **Python Azure Functions**.

---

## ✨ Features

- `@openapi` decorator — annotate once, generate full spec
- Serves `/openapi.json`, `/openapi.yaml`, and `/docs` (Swagger UI)
- Supports query/path/header parameters, requestBody, responses, tags
- Optional Pydantic integration for request/response schema inference
- Zero hard dependency on Pydantic (works with or without)

---

## 🚀 Installation

```bash
pip install azure-functions-openapi
```

For local development:

```bash
git clone https://github.com/yeongseon/azure-functions-openapi.git
cd azure-functions-openapi
pip install -e .[dev]
```

---

## ⚡ Quick Start

> Create a minimal HTTP-triggered Azure Function with auto Swagger documentation.

<details>
<summary>Click to expand quickstart steps</summary>

1. Set up environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install azure-functions azure-functions-worker azure-functions-openapi
```

2. Initialize Azure Functions project
```bash
func init hello_openapi --python
cd hello_openapi
```

3. Add `function_app.py`
<sup>(sample in full doc below)</sup>

4. Run locally:
```bash
func start
```

5. Deploy:
```bash
func azure functionapp publish <FUNCTION-APP-NAME> --python
```

**🔗 Swagger UI →** `https://<FUNCTION-APP-NAME>.azurewebsites.net/api/docs`

</details>

---

## 🧪 Example with Pydantic

```python
from pydantic import BaseModel
from azure_functions_openapi.decorator import openapi

class RequestModel(BaseModel):  name: str
class ResponseModel(BaseModel): message: str

@openapi(
    summary="Greet user (Pydantic)",
    request_model=RequestModel,
    response_model=ResponseModel,
    tags=["Example"]
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    ...
```

> Requires **Pydantic v2**.

---

## 📚 Documentation

- Full docs: [yeongseon.github.io/azure-functions-openapi](https://yeongseon.github.io/azure-functions-openapi/)
- [Quickstart](docs/usage.md)
- [Development Guide](docs/development.md)
- [Contribution Guide](docs/contributing.md)

---

## 🪪 License

MIT © 2025 Yeongseon Choe
