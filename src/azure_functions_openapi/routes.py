"""Single source of truth for the Azure Functions HTTP route prefix policy.

Shared by the spec generator, the validation bridge, the CLI, and the
public ``get_openapi_*`` helpers so they cannot drift apart.
"""

from __future__ import annotations

DEFAULT_ROUTE_PREFIX = "/api"


def normalize_route_prefix(route_prefix: str) -> str:
    """Canonicalize a user-supplied prefix.

    The Azure Functions ``host.json`` contract treats the prefix as a
    path segment without a trailing slash; an empty string means
    "no prefix is served".
    """
    prefix = (route_prefix or "").strip()
    if not prefix:
        return ""
    if not prefix.startswith("/"):
        prefix = f"/{prefix}"
    return prefix.rstrip("/")


def apply_route_prefix(path: str, prefix: str) -> str:
    """Prepend ``prefix`` to ``path`` unless ``path`` is already prefixed.

    Idempotent so that authors who write ``route="/api/users"`` are not
    double-prefixed when the spec is generated with the default ``/api``.
    """
    if not prefix:
        return path
    if path == prefix or path.startswith(f"{prefix}/"):
        return path
    return f"{prefix}{path}"
