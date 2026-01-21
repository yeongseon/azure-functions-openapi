# test/test_utils.py

from typing import Any, Dict, List, Type

from packaging import version
import pydantic
from pydantic import BaseModel, Field
import pytest

from azure_functions_openapi.utils import model_to_schema

# Determine current Pydantic version
PYDANTIC_V2 = version.parse(pydantic.__version__) >= version.parse("2.0.0")

ModelVariants: List[Type[BaseModel]]

# Define a shared model for v1 and v2 style
if PYDANTIC_V2:

    class MyV2Model(BaseModel):
        title: str = Field(..., description="The title of the item")
        done: bool = Field(default=False)

    ModelVariants = [MyV2Model]

else:

    class MyV1Model(BaseModel):
        title: str = Field(..., description="The title of the item")
        done: bool = Field(default=False)

    ModelVariants = [MyV1Model]


@pytest.mark.parametrize("model_cls", ModelVariants)
def test_model_to_schema(model_cls: Type[BaseModel]) -> None:
    """Verify that the model_to_schema function returns a valid schema for the given model class."""
    components: Dict[str, Any] = {"schemas": {}}
    schema: Dict[str, Any] = model_to_schema(model_cls, components)

    # Common schema assertions
    assert schema == {"$ref": f"#/components/schemas/{model_cls.__name__}"}
    assert model_cls.__name__ in components["schemas"]

    registered = components["schemas"][model_cls.__name__]
    assert "title" in registered or "properties" in registered
    assert "done" in registered.get("properties", {})
    assert "title" in registered.get("properties", {})
    assert "$defs" not in registered
