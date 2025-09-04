# tests/test_utils_enhanced.py

import pytest
from unittest.mock import patch
from pydantic import BaseModel, Field

from azure_functions_openapi.utils import (
    model_to_schema,
    validate_route_path,
    sanitize_operation_id
)


class SampleModel(BaseModel):
    """Sample Pydantic model for testing."""
    name: str = Field(..., description="The name of the item")
    age: int = Field(default=18, description="The age of the item")
    email: str = Field(..., description="Email address")


class TestModelToSchema:
    """Test model_to_schema function."""
    
    def test_model_to_schema_pydantic_v2(self):
        """Test model_to_schema with Pydantic v2."""
        with patch('azure_functions_openapi.utils.PYDANTIC_V2', True):
            schema = model_to_schema(SampleModel)
            
            assert isinstance(schema, dict)
            assert "properties" in schema
            assert "name" in schema["properties"]
            assert "age" in schema["properties"]
            assert "email" in schema["properties"]
            assert "required" in schema
            assert "name" in schema["required"]
            assert "email" in schema["required"]
            assert "age" not in schema["required"]  # Has default value
    
    def test_model_to_schema_pydantic_v1(self):
        """Test model_to_schema with Pydantic v1."""
        with patch('azure_functions_openapi.utils.PYDANTIC_V2', False):
            with patch.object(SampleModel, 'schema') as mock_schema:
                mock_schema.return_value = {"type": "object", "properties": {"name": {"type": "string"}}}
                
                schema = model_to_schema(SampleModel)
                
                assert schema == {"type": "object", "properties": {"name": {"type": "string"}}}
                mock_schema.assert_called_once()


class TestValidateRoutePath:
    """Test validate_route_path function."""
    
    def test_validate_route_path_valid_routes(self):
        """Test validation of valid route paths."""
        valid_routes = [
            "/api/test",
            "/users/{id}",
            "/api/v1/users/{user_id}/posts/{post_id}",
            "/api/test-with-hyphens",
            "/api/test_with_underscores",
            "/api/test with spaces",
            "/"
        ]
        
        for route in valid_routes:
            assert validate_route_path(route) is True, f"Route '{route}' should be valid"
    
    def test_validate_route_path_invalid_routes(self):
        """Test validation of invalid route paths."""
        invalid_routes = [
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
            assert validate_route_path(route) is False, f"Route '{route}' should be invalid"
    
    def test_validate_route_path_edge_cases(self):
        """Test validation of edge cases."""
        # Empty string
        assert validate_route_path("") is False
        
        # Non-string input
        assert validate_route_path(123) is False
        assert validate_route_path([]) is False
        assert validate_route_path({}) is False
        
        # Very long route
        long_route = "/" + "a" * 1000
        assert validate_route_path(long_route) is True
        
        # Route with special characters (should be invalid)
        assert validate_route_path("/api/test@#$%") is False
    
    def test_validate_route_path_case_sensitivity(self):
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
            assert validate_route_path(route) is False, f"Route '{route}' should be invalid"


class TestSanitizeOperationId:
    """Test sanitize_operation_id function."""
    
    def test_sanitize_operation_id_valid_ids(self):
        """Test sanitization of valid operation IDs."""
        valid_ids = [
            "getUser",
            "create_user",
            "updateUserProfile",
            "delete_item",
            "get_user_by_id",
            "test123",
            "a",
            "operation_id_with_underscores"
        ]
        
        for op_id in valid_ids:
            result = sanitize_operation_id(op_id)
            assert result == op_id, f"Operation ID '{op_id}' should remain unchanged"
    
    def test_sanitize_operation_id_invalid_ids(self):
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
            result = sanitize_operation_id(input_id)
            assert result == expected, f"Operation ID '{input_id}' should be sanitized to '{expected}'"
    
    def test_sanitize_operation_id_starts_with_number(self):
        """Test sanitization of operation IDs that start with numbers."""
        test_cases = [
            ("123getUser", "op_123getUser"),
            ("1user", "op_1user"),
            ("9test", "op_9test"),
        ]
        
        for input_id, expected in test_cases:
            result = sanitize_operation_id(input_id)
            assert result == expected, f"Operation ID '{input_id}' should be prefixed with 'op_'"
    
    def test_sanitize_operation_id_edge_cases(self):
        """Test sanitization of edge cases."""
        # Empty string
        assert sanitize_operation_id("") == ""
        
        # None input
        assert sanitize_operation_id(None) == ""
        
        # Non-string input
        assert sanitize_operation_id(123) == ""
        assert sanitize_operation_id([]) == ""
        assert sanitize_operation_id({}) == ""
        
        # Only special characters
        assert sanitize_operation_id("!@#$%^&*()") == ""
        
        # Only numbers
        assert sanitize_operation_id("123456") == "op_123456"
        
        # Mixed case with special characters
        result = sanitize_operation_id("Get-User@123")
        assert result == "GetUser123"
    
    def test_sanitize_operation_id_preserves_case(self):
        """Test that sanitization preserves case."""
        test_cases = [
            ("GetUser", "GetUser"),
            ("GET_USER", "GET_USER"),
            ("getUser", "getUser"),
            ("Get-User", "GetUser"),
            ("GET-USER", "GETUSER"),
        ]
        
        for input_id, expected in test_cases:
            result = sanitize_operation_id(input_id)
            assert result == expected, f"Operation ID '{input_id}' should preserve case as '{expected}'"
    
    def test_sanitize_operation_id_unicode(self):
        """Test sanitization with Unicode characters."""
        # Unicode characters should be removed
        result = sanitize_operation_id("get用户")
        assert result == "get"
        
        # Mixed ASCII and Unicode
        result = sanitize_operation_id("get用户123")
        assert result == "get123"
        
        # Only Unicode
        result = sanitize_operation_id("用户")
        assert result == ""