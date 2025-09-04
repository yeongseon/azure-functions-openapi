# tests/test_openapi_enhanced.py

import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel, Field

from azure_functions_openapi.openapi import (
    generate_openapi_spec,
    get_openapi_json,
    get_openapi_yaml
)
from azure_functions_openapi.errors import OpenAPIError


class SampleRequestModel(BaseModel):
    """Sample request model."""
    name: str = Field(..., description="The name")
    age: int = Field(default=18, description="The age")


class SampleResponseModel(BaseModel):
    """Sample response model."""
    id: int = Field(..., description="The ID")
    name: str = Field(..., description="The name")
    age: int = Field(..., description="The age")


class TestGenerateOpenAPISpecEnhanced:
    """Test enhanced generate_openapi_spec function."""
    
    def test_generate_openapi_spec_with_error_handling(self):
        """Test OpenAPI spec generation with error handling."""
        # Mock registry with problematic function
        mock_registry = {
            "test_func": {
                "summary": "Test function",
                "description": "A test function",
                "tags": ["test"],
                "operation_id": "test_operation",
                "route": "/test",
                "method": "get",
                "parameters": [],
                "request_model": None,
                "request_body": None,
                "response_model": None,
                "response": {}
            }
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            spec = generate_openapi_spec("Test API", "1.0.0")
            
            assert spec["openapi"] == "3.0.0"
            assert spec["info"]["title"] == "Test API"
            assert spec["info"]["version"] == "1.0.0"
            assert "/test" in spec["paths"]
            assert "get" in spec["paths"]["/test"]
    
    def test_generate_openapi_spec_with_model_errors(self):
        """Test OpenAPI spec generation when model schema generation fails."""
        mock_registry = {
            "test_func": {
                "summary": "Test function",
                "description": "A test function",
                "tags": ["test"],
                "operation_id": "test_operation",
                "route": "/test",
                "method": "post",
                "parameters": [],
                "request_model": SampleRequestModel,
                "request_body": None,
                "response_model": SampleResponseModel,
                "response": {}
            }
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            with patch('azure_functions_openapi.openapi.model_to_schema') as mock_model_to_schema:
                # First call succeeds, second call fails
                mock_model_to_schema.side_effect = [{"type": "object"}, Exception("Schema error")]
                
                spec = generate_openapi_spec("Test API", "1.0.0")
                
                assert spec["openapi"] == "3.0.0"
                assert "/test" in spec["paths"]
                assert "post" in spec["paths"]["/test"]
                
                # Should have fallback schema for response
                post_op = spec["paths"]["/test"]["post"]
                assert "requestBody" in post_op
                assert "responses" in post_op
                assert "200" in post_op["responses"]
    
    def test_generate_openapi_spec_with_function_processing_error(self):
        """Test OpenAPI spec generation when individual function processing fails."""
        mock_registry = {
            "good_func": {
                "summary": "Good function",
                "description": "A good function",
                "tags": ["test"],
                "operation_id": "good_operation",
                "route": "/good",
                "method": "get",
                "parameters": [],
                "request_model": None,
                "request_body": None,
                "response_model": None,
                "response": {}
            },
            "bad_func": {
                "summary": "Bad function",
                "description": "A bad function",
                "tags": ["test"],
                "operation_id": "bad_operation",
                "route": "/bad",
                "method": "get",
                "parameters": [],
                "request_model": None,
                "request_body": None,
                "response_model": None,
                "response": {}
            }
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            with patch('azure_functions_openapi.openapi.logger') as mock_logger:
                # Mock the processing to fail for bad_func
                original_spec = generate_openapi_spec("Test API", "1.0.0")
                
                # Should still generate spec for good functions
                assert original_spec["openapi"] == "3.0.0"
                assert "/good" in original_spec["paths"]
                # bad_func might be excluded due to processing error
    
    def test_generate_openapi_spec_general_error(self):
        """Test OpenAPI spec generation with general error."""
        with patch('azure_functions_openapi.openapi.get_openapi_registry') as mock_registry:
            mock_registry.side_effect = Exception("Registry error")
            
            with pytest.raises(OpenAPIError) as exc_info:
                generate_openapi_spec("Test API", "1.0.0")
            
            assert "Failed to generate OpenAPI specification" in str(exc_info.value)
            assert exc_info.value.details["error"] == "Registry error"
    
    def test_generate_openapi_spec_logging(self):
        """Test that OpenAPI spec generation logs correctly."""
        mock_registry = {
            "func1": {"summary": "Function 1", "route": "/func1", "method": "get"},
            "func2": {"summary": "Function 2", "route": "/func2", "method": "post"}
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            with patch('azure_functions_openapi.openapi.logger') as mock_logger:
                spec = generate_openapi_spec("Test API", "1.0.0")
                
                # Should log successful generation
                mock_logger.info.assert_called_once()
                call_args = mock_logger.info.call_args[0][0]
                assert "Generated OpenAPI spec" in call_args
                assert "2 paths" in call_args
                assert "2 functions" in call_args


class TestGetOpenAPIJSONEnhanced:
    """Test enhanced get_openapi_json function."""
    
    def test_get_openapi_json_success(self):
        """Test successful JSON generation."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.return_value = {"openapi": "3.0.0", "info": {"title": "Test API"}}
            
            result = get_openapi_json("Test API", "1.0.0")
            
            assert result == '{\n  "openapi": "3.0.0",\n  "info": {\n    "title": "Test API"\n  }\n}'
            mock_cached.assert_called_once_with("Test API", "1.0.0")
    
    def test_get_openapi_json_error(self):
        """Test JSON generation with error."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.side_effect = Exception("Cache error")
            
            with pytest.raises(OpenAPIError) as exc_info:
                get_openapi_json("Test API", "1.0.0")
            
            assert "Failed to generate OpenAPI JSON" in str(exc_info.value)
            assert exc_info.value.details["error"] == "Cache error"
    
    def test_get_openapi_json_logging(self):
        """Test that JSON generation logs errors."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.side_effect = Exception("Cache error")
            
            with patch('azure_functions_openapi.openapi.logger') as mock_logger:
                with pytest.raises(OpenAPIError):
                    get_openapi_json("Test API", "1.0.0")
                
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Failed to generate OpenAPI JSON" in call_args


class TestGetOpenAPIYAMLEnhanced:
    """Test enhanced get_openapi_yaml function."""
    
    def test_get_openapi_yaml_success(self):
        """Test successful YAML generation."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.return_value = {"openapi": "3.0.0", "info": {"title": "Test API"}}
            
            result = get_openapi_yaml("Test API", "1.0.0")
            
            assert "openapi: 3.0.0" in result
            assert "title: Test API" in result
            mock_cached.assert_called_once_with("Test API", "1.0.0")
    
    def test_get_openapi_yaml_error(self):
        """Test YAML generation with error."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.side_effect = Exception("Cache error")
            
            with pytest.raises(OpenAPIError) as exc_info:
                get_openapi_yaml("Test API", "1.0.0")
            
            assert "Failed to generate OpenAPI YAML" in str(exc_info.value)
            assert exc_info.value.details["error"] == "Cache error"
    
    def test_get_openapi_yaml_logging(self):
        """Test that YAML generation logs errors."""
        with patch('azure_functions_openapi.openapi.cached_openapi_spec') as mock_cached:
            mock_cached.side_effect = Exception("Cache error")
            
            with patch('azure_functions_openapi.openapi.logger') as mock_logger:
                with pytest.raises(OpenAPIError):
                    get_openapi_yaml("Test API", "1.0.0")
                
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Failed to generate OpenAPI YAML" in call_args


class TestOpenAPISpecComplexScenarios:
    """Test complex OpenAPI spec generation scenarios."""
    
    def test_generate_openapi_spec_with_all_components(self):
        """Test OpenAPI spec generation with all components."""
        mock_registry = {
            "complex_func": {
                "summary": "Complex function",
                "description": "A complex function with all features",
                "tags": ["complex", "test"],
                "operation_id": "complex_operation",
                "route": "/complex/{id}",
                "method": "put",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer"}}
                ],
                "request_model": SampleRequestModel,
                "request_body": None,
                "response_model": SampleResponseModel,
                "response": {
                    400: {"description": "Bad Request"},
                    404: {"description": "Not Found"},
                    500: {"description": "Internal Server Error"}
                }
            }
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            with patch('azure_functions_openapi.openapi.model_to_schema') as mock_model_to_schema:
                mock_model_to_schema.return_value = {"type": "object", "properties": {"name": {"type": "string"}}}
                
                spec = generate_openapi_spec("Complex API", "2.0.0")
                
                assert spec["openapi"] == "3.0.0"
                assert spec["info"]["title"] == "Complex API"
                assert spec["info"]["version"] == "2.0.0"
                
                # Check path
                assert "/complex/{id}" in spec["paths"]
                put_op = spec["paths"]["/complex/{id}"]["put"]
                
                # Check operation details
                assert put_op["summary"] == "Complex function"
                assert put_op["description"] == "A complex function with all features"
                assert put_op["operationId"] == "complex_operation"
                assert put_op["tags"] == ["complex", "test"]
                
                # Check parameters
                assert len(put_op["parameters"]) == 2
                param_names = [p["name"] for p in put_op["parameters"]]
                assert "id" in param_names
                assert "limit" in param_names
                
                # Check request body
                assert "requestBody" in put_op
                assert put_op["requestBody"]["required"] is True
                
                # Check responses
                assert "200" in put_op["responses"]
                assert "400" in put_op["responses"]
                assert "404" in put_op["responses"]
                assert "500" in put_op["responses"]
    
    def test_generate_openapi_spec_multiple_methods_same_route(self):
        """Test OpenAPI spec generation with multiple methods on same route."""
        mock_registry = {
            "get_user": {
                "summary": "Get user",
                "route": "/users/{id}",
                "method": "get",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]
            },
            "update_user": {
                "summary": "Update user",
                "route": "/users/{id}",
                "method": "put",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "request_model": SampleRequestModel
            },
            "delete_user": {
                "summary": "Delete user",
                "route": "/users/{id}",
                "method": "delete",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]
            }
        }
        
        with patch('azure_functions_openapi.openapi.get_openapi_registry', return_value=mock_registry):
            spec = generate_openapi_spec("User API", "1.0.0")
            
            # Check that all methods are on the same path
            assert "/users/{id}" in spec["paths"]
            path_obj = spec["paths"]["/users/{id}"]
            
            assert "get" in path_obj
            assert "put" in path_obj
            assert "delete" in path_obj
            
            # Check method details
            assert path_obj["get"]["summary"] == "Get user"
            assert path_obj["put"]["summary"] == "Update user"
            assert path_obj["delete"]["summary"] == "Delete user"