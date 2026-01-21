# tests/test_utils_enhanced.py

from typing import Any, Dict, cast
from unittest.mock import patch

from pydantic import BaseModel, Field

from azure_functions_openapi.utils import (
    model_to_schema,
    sanitize_operation_id,
    validate_route_path,
)

validate_route_path_any = cast(Any, validate_route_path)
sanitize_operation_id_any = cast(Any, sanitize_operation_id)


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""

    name: str = Field(..., description="The name of the item")
    age: int = Field(default=18, description="The age of the item")
    email: str = Field(..., description="Email address")


class TestModelToSchema:
    """Test model_to_schema function."""

    def test_model_to_schema_pydantic_v2(self) -> None:
        """Test model_to_schema with Pydantic v2."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            components: Dict[str, Dict[str, Any]] = {"schemas": {}}
            schema = model_to_schema(SampleModel, components)

            assert schema == {"$ref": "#/components/schemas/SampleModel"}
            registered = components["schemas"]["SampleModel"]
            assert "properties" in registered
            assert "name" in registered["properties"]
            assert "age" in registered["properties"]
            assert "email" in registered["properties"]
            assert "required" in registered
            assert "name" in registered["required"]
            assert "email" in registered["required"]
            assert "age" not in registered["required"]  # Has default value

    def test_model_to_schema_pydantic_v1(self) -> None:
        """Test model_to_schema with Pydantic v1."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", False):
            with patch.object(SampleModel, "schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                }

                components: Dict[str, Dict[str, Any]] = {"schemas": {}}
                schema = model_to_schema(SampleModel, components)

                assert schema == {"$ref": "#/components/schemas/SampleModel"}
                assert components["schemas"]["SampleModel"] == {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                }
                mock_schema.assert_called_once()

    def test_model_to_schema_rewrites_defs_v2(self) -> None:
        """Test that $defs and refs are rewritten for OpenAPI."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "array",
                    "items": {"$ref": "#/$defs/Item"},
                    "$defs": {
                        "Item": {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}},
                        }
                    },
                }

                components: Dict[str, Dict[str, Any]] = {"schemas": {}}
                schema = model_to_schema(SampleModel, components)

                assert schema == {"$ref": "#/components/schemas/SampleModel"}
                registered = components["schemas"]["SampleModel"]
                assert "$defs" not in registered
                assert registered["items"]["$ref"] == "#/components/schemas/Item"
                assert "Item" in components["schemas"]

    def test_model_to_schema_rewrites_definitions_v1(self) -> None:
        """Test that v1 definitions are rewritten for OpenAPI."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", False):
            with patch.object(SampleModel, "schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Item"},
                    "definitions": {
                        "Item": {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}},
                        }
                    },
                }

                components: Dict[str, Dict[str, Any]] = {"schemas": {}}
                schema = model_to_schema(SampleModel, components)

                assert schema == {"$ref": "#/components/schemas/SampleModel"}
                registered = components["schemas"]["SampleModel"]
                assert "definitions" not in registered
                assert registered["items"]["$ref"] == "#/components/schemas/Item"
                assert "Item" in components["schemas"]


class TestValidateRoutePath:
    """Test validate_route_path function."""

    def test_validate_route_path_valid_routes(self) -> None:
        """Test validation of valid route paths."""
        valid_routes = [
            "/api/test",
            "/users/{id}",
            "/api/v1/users/{user_id}/posts/{post_id}",
            "/api/test-with-hyphens",
            "/api/test_with_underscores",
            "/api/test with spaces",
            "/",
        ]

        for route in valid_routes:
            assert validate_route_path_any(route) is True, f"Route '{route}' should be valid"

    def test_validate_route_path_invalid_routes(self) -> None:
        """Test validation of invalid route paths."""
        invalid_routes: list[Any] = [
            None,
            "",
            "not_starting_with_slash",
            "/api/../test",  # Path traversal
            "/api/<script>alert('xss')</script>",  # XSS attempt
            "/api/javascript:alert('xss')",  # JavaScript injection
            "/api/data:text/html,<script>alert('xss')</script>",  # Data URI injection
            "/api/test?param=<script>",  # XSS in query
            "/api/test#<script>",  # XSS in fragment
        ]

        for route in invalid_routes:
            assert validate_route_path_any(route) is False, f"Route '{route}' should be invalid"

    def test_validate_route_path_edge_cases(self) -> None:
        """Test validation of edge cases."""
        # Empty string
        assert validate_route_path_any("") is False

        # Non-string input
        non_string_routes: list[Any] = [123, [], {}]
        for route in non_string_routes:
            assert validate_route_path_any(route) is False

        # Very long route
        long_route = "/" + "a" * 1000
        assert validate_route_path_any(long_route) is True

        # Route with special characters (should be invalid)
        assert validate_route_path_any("/api/test@#$%") is False

    def test_validate_route_path_case_sensitivity(self) -> None:
        """Test that validation is case sensitive for dangerous patterns."""
        # These should be caught regardless of case
        dangerous_routes = [
            "/api/../test",
            "/api/..\\test",  # Windows path traversal
            "/api/<SCRIPT>alert('xss')</SCRIPT>",  # Uppercase XSS
            "/api/JAVASCRIPT:alert('xss')",  # Uppercase JavaScript
            "/api/DATA:text/html,<script>alert('xss')</script>",  # Uppercase Data URI
        ]

        for route in dangerous_routes:
            assert validate_route_path_any(route) is False, f"Route '{route}' should be invalid"


class TestSanitizeOperationId:
    """Test sanitize_operation_id function."""

    def test_sanitize_operation_id_valid_ids(self) -> None:
        """Test sanitization of valid operation IDs."""
        valid_ids = [
            "getUser",
            "create_user",
            "updateUserProfile",
            "delete_item",
            "get_user_by_id",
            "test123",
            "a",
            "operation_id_with_underscores",
        ]

        for op_id in valid_ids:
            result = sanitize_operation_id_any(op_id)
            assert result == op_id, f"Operation ID '{op_id}' should remain unchanged"

    def test_sanitize_operation_id_invalid_ids(self) -> None:
        """Test sanitization of invalid operation IDs."""
        test_cases = [
            ("get-user", "getuser"),  # Hyphens removed
            ("get.user", "getuser"),  # Dots removed
            ("get user", "getuser"),  # Spaces removed
            ("get@user", "getuser"),  # Special chars removed
            ("get#user", "getuser"),  # Special chars removed
            ("get$user", "getuser"),  # Special chars removed
            ("get%user", "getuser"),  # Special chars removed
            ("get&user", "getuser"),  # Special chars removed
            ("get*user", "getuser"),  # Special chars removed
            ("get+user", "getuser"),  # Special chars removed
            ("get=user", "getuser"),  # Special chars removed
            ("get?user", "getuser"),  # Special chars removed
            ("get!user", "getuser"),  # Special chars removed
            ("get^user", "getuser"),  # Special chars removed
            ("get~user", "getuser"),  # Special chars removed
            ("get`user", "getuser"),  # Special chars removed
            ("get|user", "getuser"),  # Special chars removed
            ("get\\user", "getuser"),  # Special chars removed
            ("get/user", "getuser"),  # Special chars removed
            ("get<user", "getuser"),  # Special chars removed
            ("get>user", "getuser"),  # Special chars removed
            ("get[user", "getuser"),  # Special chars removed
            ("get]user", "getuser"),  # Special chars removed
            ("get{user", "getuser"),  # Special chars removed
            ("get}user", "getuser"),  # Special chars removed
            ("get(user", "getuser"),  # Special chars removed
            ("get)user", "getuser"),  # Special chars removed
        ]

        for input_id, expected in test_cases:
            result = sanitize_operation_id_any(input_id)
            assert (
                result == expected
            ), f"Operation ID '{input_id}' should be sanitized to '{expected}'"

    def test_sanitize_operation_id_starts_with_number(self) -> None:
        """Test sanitization of operation IDs that start with numbers."""
        test_cases = [
            ("123getUser", "op_123getUser"),
            ("1user", "op_1user"),
            ("9test", "op_9test"),
        ]

        for input_id, expected in test_cases:
            result = sanitize_operation_id_any(input_id)
            assert result == expected, f"Operation ID '{input_id}' should be prefixed with 'op_'"

    def test_sanitize_operation_id_edge_cases(self) -> None:
        """Test sanitization of edge cases."""
        # Empty string
        assert sanitize_operation_id_any("") == ""

        invalid_ids: list[Any] = [None, 123, [], {}]
        for op_id in invalid_ids:
            assert sanitize_operation_id_any(op_id) == ""

        # Only special characters
        assert sanitize_operation_id_any("!@#$%^&*()") == ""

        # Only numbers
        assert sanitize_operation_id_any("123456") == "op_123456"

        # Mixed case with special characters
        result = sanitize_operation_id_any("Get-User@123")
        assert result == "GetUser123"

    def test_sanitize_operation_id_preserves_case(self) -> None:
        """Test that sanitization preserves case."""
        test_cases = [
            ("GetUser", "GetUser"),
            ("GET_USER", "GET_USER"),
            ("getUser", "getUser"),
            ("Get-User", "GetUser"),
            ("GET-USER", "GETUSER"),
        ]

        for input_id, expected in test_cases:
            result = sanitize_operation_id_any(input_id)
            assert (
                result == expected
            ), f"Operation ID '{input_id}' should preserve case as '{expected}'"

    def test_sanitize_operation_id_unicode(self) -> None:
        """Test sanitization with Unicode characters."""
        # Unicode characters should be removed
        result = sanitize_operation_id_any("get用户")
        assert result == "get"

        # Mixed ASCII and Unicode
        result = sanitize_operation_id_any("get用户123")
        assert result == "get123"

        # Only Unicode
        result = sanitize_operation_id_any("用户")
        assert result == ""
