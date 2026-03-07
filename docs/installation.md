# Installation

This project supports the **Azure Functions Python v2 programming model**.

## Requirements

- Python 3.10+
- Azure Functions Core Tools
- Azure Functions Python **v2** (`func.FunctionApp` with decorators)

> This library is not compatible with the legacy `function.json`-based v1 model.

## Install the Package

```bash
pip install azure-functions-openapi
```

Then ensure your Function App dependencies include:

```text
azure-functions
azure-functions-openapi
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Azure Functions Core Tools

Install Azure Functions Core Tools using the official Microsoft instructions:

- Windows: https://learn.microsoft.com/azure/azure-functions/functions-run-local
- macOS: https://learn.microsoft.com/azure/azure-functions/functions-run-local
- Linux: https://learn.microsoft.com/azure/azure-functions/functions-run-local
