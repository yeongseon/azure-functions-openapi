# src/azure_functions_openapi/utils.py
from typing import Any, Dict, cast

from packaging import version
import pydantic

PYDANTIC_V2 = version.parse(pydantic.__version__) >= version.parse("2.0.0")


def model_to_schema(model_cls: Any) -> Dict[str, Any]:
    """Return JSON schema from a Pydantic model class.
    Parameters:
        model_cls: Pydantic model class.
    Returns:
        Dict[str, Any]: JSON schema representation of the model.
    """

    if PYDANTIC_V2:
        return cast(Dict[str, Any], model_cls.model_json_schema())
    return cast(Dict[str, Any], model_cls.schema())
