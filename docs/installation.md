# Installation

This project supports Python-based Azure Functions using the **Programming Model v2**.

---

## Table of Contents

- Requirements
- Installation
- Azure Functions Core Tools (Platform Notes)
- Local Development

---

## Requirements

- Python **3.10+** (3.10–3.12 tested)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- Azure Functions Python Programming Model **v2**

> This library is not compatible with the legacy v1 model.

---

## Installation

Install the package via pip:

```bash
pip install azure-functions-openapi
```

Then ensure your `requirements.txt` includes:

```
azure-functions
azure-functions-openapi
```

If you're developing locally:

```bash
pip install -e .[dev]
```

---

## Azure Functions Core Tools (Platform Notes)

Install Azure Functions Core Tools using the official instructions:

- Windows: https://learn.microsoft.com/azure/azure-functions/functions-run-local
- macOS: https://learn.microsoft.com/azure/azure-functions/functions-run-local
- Linux: https://learn.microsoft.com/azure/azure-functions/functions-run-local

Verify installation:

```bash
func --version
```

---

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```
