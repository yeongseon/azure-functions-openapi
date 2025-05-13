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
    schema: Dict[str, Any] = model_to_schema(model_cls)

    # Common schema assertions
    assert isinstance(schema, dict)
    assert "title" in schema or "properties" in schema
    assert "done" in schema.get("properties", {})
    assert "title" in schema.get("properties", {})
