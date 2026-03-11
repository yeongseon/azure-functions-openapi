# azure-functions-openapi

语言: [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

[![PyPI](https://img.shields.io/pypi/v/azure-functions-openapi.svg)](https://pypi.org/project/azure-functions-openapi/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/azure-functions-openapi/)
[![CI](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/ci-test.yml)
[![Security Scans](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml/badge.svg)](https://github.com/yeongseon/azure-functions-openapi/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yeongseon/azure-functions-openapi/branch/main/graph/badge.svg)](https://codecov.io/gh/yeongseon/azure-functions-openapi)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-blue)](https://yeongseon.github.io/azure-functions-openapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

为 **Azure Functions Python v2 编程模型**提供 OpenAPI（Swagger）文档生成和 Swagger UI。

## Scope

- Azure Functions Python **v2 编程模型**
- 基于 decorator 的 `func.FunctionApp()` 应用
- 使用 `@openapi` 记录文档的 HTTP 触发函数
- 可选的 Pydantic schema 生成（同时支持 Pydantic v1 和 v2）

此包**不支持**传统的基于 `function.json` 的 v1 编程模型。

## Features

- 用于 operation 元数据的 `@openapi` decorator
- `/openapi.json`、`/openapi.yaml` 和 `/docs` 端点
- 支持 query、path、header、body 和 response schema
- 带有安全默认值的 Swagger UI helper
- 用于生成和校验工作流的 CLI 工具

## Demo

代表性的 `hello` 示例展示了采用该库后的完整效果：

- 你为 Azure Functions v2 的 HTTP 处理函数添加 `@openapi`。
- 该包会为该路由生成真实的 OpenAPI 文档。
- 同一路由会被渲染为 Swagger UI，便于在浏览器中查看。

### Generated Spec Result

生成的 OpenAPI 文件来自同一次示例运行，并被捕获为静态预览。因此，此 README 展示的就是代表性函数实际生成的文档。

![OpenAPI spec preview](/root/Github/azure-functions/azure-functions-openapi/docs/assets/hello_openapi_spec_preview.png)

### Swagger UI Result

下面的网页预览也来自同一个代表性示例，并由该示例流程生成的 Swagger UI 页面自动渲染和截图得到。

![OpenAPI Swagger UI preview](/root/Github/azure-functions/azure-functions-openapi/docs/assets/hello_openapi_swagger_ui_preview.png)

## Installation

```bash
pip install azure-functions-openapi
```

你的 Function App 依赖应包含：

```text
azure-functions
azure-functions-openapi
```

## Quick Start

```python
import json

import azure.functions as func

from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui


app = func.FunctionApp()


@app.function_name(name="http_trigger")
@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
@openapi(
    summary="Greet user",
    route="/api/http_trigger",
    method="post",
    request_body={
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    },
    response={
        200: {
            "description": "Successful greeting",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    }
                }
            },
        }
    },
    tags=["Example"],
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    name = data.get("name", "world")
    return func.HttpResponse(
        json.dumps({"message": f"Hello, {name}!"}),
        mimetype="application/json",
    )

@app.function_name(name="openapi_json")
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_json(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_json(
        title="Sample API",
        description="OpenAPI document for the Sample API.",
    )


@app.function_name(name="openapi_yaml")
@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_yaml(req: func.HttpRequest) -> func.HttpResponse:
    return get_openapi_yaml(
        title="Sample API",
        description="OpenAPI document for the Sample API.",
    )


@app.function_name(name="swagger_ui")
@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

可使用 Azure Functions Core Tools 在本地运行：

```bash
func start
```

## Documentation

- 完整文档: [yeongseon.github.io/azure-functions-openapi](https://yeongseon.github.io/azure-functions-openapi/)
- 经过 smoke test 的示例: `examples/`
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api.md)
- [CLI Guide](docs/cli.md)

## Disclaimer

本项目是独立的社区项目，与 Microsoft 没有关联，也未获得 Microsoft 的认可或维护。

Azure 和 Azure Functions 是 Microsoft Corporation 的商标。

## License

MIT
