from azure_functions_openapi.swagger_ui import render_swagger_ui


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
