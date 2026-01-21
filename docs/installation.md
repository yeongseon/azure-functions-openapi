# Installation

This project supports Python-based Azure Functions using the **Programming Model v2**.

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
