# tests/test_utils_enhanced.py

from typing import Any, Dict, cast
from unittest.mock import patch

from pydantic import BaseModel, Field

from azure_functions_openapi.utils import (
    _collect_schemas,
    _resolve_name_collision,
    _rewrite_ref,
    _rewrite_refs_with_map,
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

    def test_model_to_schema_initializes_components_when_missing(self) -> None:
        schema = model_to_schema(SampleModel, None)

        assert schema == {"$ref": "#/components/schemas/SampleModel"}

    def test_model_to_schema_resolves_name_collisions(self) -> None:
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {"child": {"$ref": "#/components/schemas/Child"}},
                    "$defs": {
                        "Child": {
                            "type": "object",
                            "properties": {"id": {"type": "integer"}},
                        }
                    },
                }

                components: Dict[str, Dict[str, Any]] = {
                    "schemas": {
                        "SampleModel": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}},
                        },
                        "Child": {"type": "object", "properties": {"legacy": {"type": "string"}}},
                    }
                }
                schema = model_to_schema(SampleModel, components)

                assert schema == {"$ref": "#/components/schemas/SampleModel_2"}
                assert "SampleModel_2" in components["schemas"]
                assert "Child_2" in components["schemas"]
                child_ref = components["schemas"]["SampleModel_2"]["properties"]["child"]["$ref"]
                assert child_ref == "#/components/schemas/Child_2"


class TestUtilsInternals:
    def test_collect_schemas_skips_non_dict_definitions_and_hoists_nested_defs(self) -> None:
        normalized, collected = _collect_schemas(
            {
                "type": "array",
                "items": {"$ref": "#/$defs/Item"},
                "$defs": {
                    "Item": {
                        "type": "object",
                        "properties": {"child": {"$ref": "#/$defs/Nested"}},
                        "$defs": {"Nested": {"type": "string"}},
                    },
                    "Ignored": "not-a-dict",
                },
            }
        )

        assert normalized["items"]["$ref"] == "#/components/schemas/Item"
        assert "Item" in collected
        assert "Nested" in collected
        assert "Ignored" not in collected

    def test_resolve_name_collision_uses_suffix_and_reuses_identical_schema(self) -> None:
        existing = {
            "Thing": {"type": "object", "properties": {"id": {"type": "integer"}}},
            "Thing_2": {"type": "object", "properties": {"legacy": {"type": "string"}}},
        }

        assert _resolve_name_collision("Thing", existing["Thing"], existing) == "Thing"
        assert (
            _resolve_name_collision(
                "Thing",
                {"type": "object", "properties": {"legacy": {"type": "string"}}},
                existing,
            )
            == "Thing_2"
        )
        assert (
            _resolve_name_collision(
                "Thing",
                {"type": "object", "properties": {"name": {"type": "string"}}},
                existing,
            )
            == "Thing_3"
        )

    def test_rewrite_refs_with_map_handles_lists_and_empty_map(self) -> None:
        payload: Dict[str, Any] = {
            "items": [
                {"$ref": "#/components/schemas/Thing"},
                {"nested": {"$ref": "#/components/schemas/Other"}},
            ]
        }

        assert _rewrite_refs_with_map(payload, {}) == payload

        rewritten = _rewrite_refs_with_map(payload, {"Thing": "Thing_2", "Other": "Other_2"})
        assert rewritten["items"][0]["$ref"] == "#/components/schemas/Thing_2"
        assert rewritten["items"][1]["nested"]["$ref"] == "#/components/schemas/Other_2"


class TestValidateRoutePath:
    """Test validate_route_path function."""

    def test_validate_route_path_valid_routes(self) -> None:
        """Test validation of valid route paths."""
        valid_routes = [
            "hello",
            "todos/{id}",
            "/api/test",
            "/users/{id}",
            "/api/v1/users/{user_id}/posts/{post_id}",
            "/api/test-with-hyphens",
            "/api/test_with_underscores",
            "/",
        ]

        for route in valid_routes:
            assert validate_route_path_any(route) is True, f"Route '{route}' should be valid"

    def test_validate_route_path_invalid_routes(self) -> None:
        """Test validation of invalid route paths."""
        invalid_routes: list[Any] = [
            None,
            "",
            "api/test?param=1",
            "/api/../test",  # Path traversal
            "/api/<script>alert('xss')</script>",  # XSS attempt
            "/api/javascript:alert('xss')",  # JavaScript injection
            "/api/data:text/html,<script>alert('xss')</script>",  # Data URI injection
            "/api/test?param=<script>",  # XSS in query
            "/api/test#<script>",  # XSS in fragment
            "/api/test with spaces",  # Whitespace in route
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
            assert result == expected, (
                f"Operation ID '{input_id}' should be sanitized to '{expected}'"
            )

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
            assert result == expected, (
                f"Operation ID '{input_id}' should preserve case as '{expected}'"
            )

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


class TestRewriteRef:
    """Test _rewrite_ref function."""

    def test_rewrite_defs_ref(self) -> None:
        assert _rewrite_ref("#/$defs/Foo") == "#/components/schemas/Foo"

    def test_rewrite_definitions_ref(self) -> None:
        assert _rewrite_ref("#/definitions/Bar") == "#/components/schemas/Bar"

    def test_passthrough_other_ref(self) -> None:
        assert _rewrite_ref("#/components/schemas/Baz") == "#/components/schemas/Baz"

    def test_passthrough_unknown_ref(self) -> None:
        assert _rewrite_ref("#/external/Something") == "#/external/Something"


class TestCollectSchemas:
    """Test _collect_schemas function."""

    def test_non_dict_definition_skipped(self) -> None:
        """Non-dict values in $defs should be skipped."""
        schema: Dict[str, Any] = {
            "type": "object",
            "$defs": {
                "Good": {"type": "string"},
                "Bad": "not_a_dict",
                "AlsoBad": 42,
            },
        }
        normalized, collected = _collect_schemas(schema)
        assert "Good" in collected
        assert "Bad" not in collected
        assert "AlsoBad" not in collected

    def test_nested_definitions_collected(self) -> None:
        """Definitions nested inside other definitions should be recursively collected."""
        schema: Dict[str, Any] = {
            "type": "object",
            "$defs": {
                "Outer": {
                    "type": "object",
                    "properties": {"inner": {"$ref": "#/$defs/Inner"}},
                    "$defs": {
                        "Inner": {"type": "string"},
                    },
                },
            },
        }
        normalized, collected = _collect_schemas(schema)
        assert "Outer" in collected
        assert "Inner" in collected
        # Outer should not retain $defs after processing
        assert "$defs" not in collected["Outer"]

    def test_empty_definitions(self) -> None:
        schema: Dict[str, Any] = {"type": "object", "properties": {"id": {"type": "integer"}}}
        normalized, collected = _collect_schemas(schema)
        assert collected == {}
        assert normalized["type"] == "object"


class TestResolveNameCollision:
    """Test _resolve_name_collision function."""

    def test_no_collision(self) -> None:
        existing: Dict[str, Dict[str, Any]] = {}
        assert _resolve_name_collision("Foo", {"type": "string"}, existing) == "Foo"

    def test_same_name_identical_schema(self) -> None:
        schema: Dict[str, Any] = {"type": "string"}
        existing: Dict[str, Dict[str, Any]] = {"Foo": {"type": "string"}}
        assert _resolve_name_collision("Foo", schema, existing) == "Foo"

    def test_collision_different_schema(self) -> None:
        schema: Dict[str, Any] = {"type": "integer"}
        existing: Dict[str, Dict[str, Any]] = {"Foo": {"type": "string"}}
        assert _resolve_name_collision("Foo", schema, existing) == "Foo_2"

    def test_collision_cascading(self) -> None:
        """When Foo and Foo_2 are both taken with different schemas, returns Foo_3."""
        schema: Dict[str, Any] = {"type": "boolean"}
        existing: Dict[str, Dict[str, Any]] = {
            "Foo": {"type": "string"},
            "Foo_2": {"type": "integer"},
        }
        assert _resolve_name_collision("Foo", schema, existing) == "Foo_3"

    def test_collision_candidate_identical(self) -> None:
        """When Foo is taken but Foo_2 has identical schema, returns Foo_2."""
        schema: Dict[str, Any] = {"type": "integer"}
        existing: Dict[str, Dict[str, Any]] = {
            "Foo": {"type": "string"},
            "Foo_2": {"type": "integer"},
        }
        assert _resolve_name_collision("Foo", schema, existing) == "Foo_2"


class TestRewriteRefsWithMap:
    """Test _rewrite_refs_with_map function."""

    def test_empty_name_map_returns_unchanged(self) -> None:
        obj: Dict[str, Any] = {"$ref": "#/components/schemas/Foo"}
        result = _rewrite_refs_with_map(obj, {})
        assert result == obj

    def test_rewrites_matching_ref(self) -> None:
        obj: Dict[str, Any] = {"$ref": "#/components/schemas/Foo"}
        result = _rewrite_refs_with_map(obj, {"Foo": "Foo_2"})
        assert result == {"$ref": "#/components/schemas/Foo_2"}

    def test_preserves_ref_not_in_map(self) -> None:
        obj: Dict[str, Any] = {"$ref": "#/components/schemas/Bar"}
        result = _rewrite_refs_with_map(obj, {"Foo": "Foo_2"})
        assert result == {"$ref": "#/components/schemas/Bar"}

    def test_preserves_non_components_ref(self) -> None:
        obj: Dict[str, Any] = {"$ref": "#/external/Foo"}
        result = _rewrite_refs_with_map(obj, {"Foo": "Foo_2"})
        assert result == {"$ref": "#/external/Foo"}

    def test_rewrites_refs_in_list(self) -> None:
        obj = [
            {"$ref": "#/components/schemas/Foo"},
            {"$ref": "#/components/schemas/Bar"},
        ]
        result = _rewrite_refs_with_map(obj, {"Foo": "Foo_2"})
        assert result == [
            {"$ref": "#/components/schemas/Foo_2"},
            {"$ref": "#/components/schemas/Bar"},
        ]

    def test_scalar_returned_unchanged(self) -> None:
        assert _rewrite_refs_with_map("hello", {"Foo": "Foo_2"}) == "hello"
        assert _rewrite_refs_with_map(42, {"Foo": "Foo_2"}) == 42

    def test_nested_dict_rewrite(self) -> None:
        obj: Dict[str, Any] = {
            "properties": {
                "child": {"$ref": "#/components/schemas/Foo"},
            }
        }
        result = _rewrite_refs_with_map(obj, {"Foo": "Foo_2"})
        assert result["properties"]["child"]["$ref"] == "#/components/schemas/Foo_2"


class TestModelToSchemaCollisionPath:
    """Test model_to_schema name collision and components=None paths."""

    def test_components_none_creates_internally(self) -> None:
        """model_to_schema(model, None) should work without error."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                }
                result = model_to_schema(SampleModel, None)
                assert result == {"$ref": "#/components/schemas/SampleModel"}

    def test_name_collision_triggers_rename(self) -> None:
        """When schema name collides with existing different schema, it gets renamed."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                }
                # Pre-populate with a different schema under the same name
                components: Dict[str, Any] = {
                    "schemas": {
                        "SampleModel": {
                            "type": "object",
                            "properties": {"other": {"type": "string"}},
                        }
                    }
                }
                result = model_to_schema(SampleModel, components)

                # Should be renamed to SampleModel_2
                assert result == {"$ref": "#/components/schemas/SampleModel_2"}
                assert "SampleModel_2" in components["schemas"]
                # Original should be preserved
                other_type = components["schemas"]["SampleModel"]["properties"]["other"]["type"]
                assert other_type == "string"

    def test_identical_schema_no_overwrite(self) -> None:
        """When schema already exists with identical content, no rename or overwrite."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                schema_content: Dict[str, Any] = {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                }
                mock_schema.return_value = dict(schema_content)
                # Pre-populate with identical schema
                components: Dict[str, Any] = {
                    "schemas": {"SampleModel": dict(schema_content)}
                }
                result = model_to_schema(SampleModel, components)

                assert result == {"$ref": "#/components/schemas/SampleModel"}
                # Should still be the same content, no _2 variant
                assert "SampleModel_2" not in components["schemas"]

    def test_name_collision_with_nested_refs_rewritten(self) -> None:
        """When collision occurs, $refs in the schema body are also rewritten."""
        with patch("azure_functions_openapi.utils.PYDANTIC_V2", True):
            with patch.object(SampleModel, "model_json_schema") as mock_schema:
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {
                        "child": {"$ref": "#/components/schemas/Child"},
                    },
                    "$defs": {
                        "Child": {"type": "string"},
                    },
                }
                # Pre-populate Child with a different schema to force collision
                components: Dict[str, Any] = {
                    "schemas": {
                        "Child": {"type": "integer"},
                    }
                }
                result = model_to_schema(SampleModel, components)

                assert result == {"$ref": "#/components/schemas/SampleModel"}
                # Child should be renamed to Child_2
                assert "Child_2" in components["schemas"]
                # The ref in SampleModel should point to Child_2
                registered = components["schemas"]["SampleModel"]
                assert registered["properties"]["child"]["$ref"] == "#/components/schemas/Child_2"
