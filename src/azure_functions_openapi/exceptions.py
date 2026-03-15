# src/azure_functions_openapi/exceptions.py
from __future__ import annotations


class OpenAPISpecConfigError(ValueError):
    """Raised for caller-fixable configuration errors such as an unsupported
    OpenAPI version or conflicting security scheme definitions.

    Subclasses :class:`ValueError` so existing ``except ValueError`` call-sites
    continue to work without changes.
    """
