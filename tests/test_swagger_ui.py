from azure_functions_openapi.swagger_ui import (
    _SWAGGER_UI_DIST_VERSION,
    render_swagger_ui,
)


def test_render_swagger_ui_returns_html_response() -> None:
    """Verify that the Swagger UI HTML response is correctly rendered."""
    # When
    response = render_swagger_ui()

    # Then
    assert response is not None
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b'<div id="swagger-ui"></div>' in response.get_body()
    assert b"SwaggerUIBundle" in response.get_body()
    assert b"/api/openapi.json" in response.get_body()


def test_render_swagger_ui_pins_swagger_ui_dist_version() -> None:
    # Given
    response = render_swagger_ui()
    body = response.get_body()
    pinned_base = (
        f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{_SWAGGER_UI_DIST_VERSION}".encode()
    )

    # Then
    assert pinned_base + b"/swagger-ui.css" in body
    assert pinned_base + b"/swagger-ui-bundle.js" in body
    assert b"swagger-ui-dist/swagger-ui" not in body
