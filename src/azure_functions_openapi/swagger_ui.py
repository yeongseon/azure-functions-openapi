from azure.functions import HttpResponse


def render_swagger_ui() -> HttpResponse:
    html_content = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Swagger UI</title>
        <link rel="stylesheet" 
              type="text/css" 
              href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
        <script>
          const ui = SwaggerUIBundle({
            url: '/api/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis],
            layout: 'BaseLayout'
          });
        </script>
      </body>
    </html>
    """
    return HttpResponse(html_content, mimetype="text/html")
