"""Tests for the public API surface of azure-functions-openapi."""

import azure_functions_openapi


class TestAPISurface:
    """Verify __all__ matches exactly the declared public names."""

    def test_all_exports(self) -> None:
        assert set(azure_functions_openapi.__all__) == {
            "__version__",
            "OPENAPI_VERSION_3_0",
            "OPENAPI_VERSION_3_1",
            "OpenAPISpecConfigError",
            "generate_openapi_spec",
            "get_openapi_json",
            "get_openapi_yaml",
            "openapi",
            "render_swagger_ui",
        }

    def test_version_is_0_15_1(self) -> None:
        assert azure_functions_openapi.__version__ == "0.15.1"

    def test_version_is_string(self) -> None:
        assert isinstance(azure_functions_openapi.__version__, str)

    def test_public_names_are_importable(self) -> None:
        from azure_functions_openapi import (  # noqa: F401
            OPENAPI_VERSION_3_0,
            OPENAPI_VERSION_3_1,
            OpenAPISpecConfigError,
            generate_openapi_spec,
            get_openapi_json,
            get_openapi_yaml,
            openapi,
            render_swagger_ui,
        )

    def test_openapi_is_importable_module(self) -> None:
        import types
        assert isinstance(azure_functions_openapi.openapi, types.ModuleType)

    def test_generate_openapi_spec_is_callable(self) -> None:
        assert callable(azure_functions_openapi.generate_openapi_spec)

    def test_openapi_spec_config_error_is_exception(self) -> None:
        assert issubclass(azure_functions_openapi.OpenAPISpecConfigError, Exception)
