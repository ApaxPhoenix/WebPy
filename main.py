from webpy import WebPy
from middleware import Middleware

# Instantiate the WebPyApp wrapper and middleware
web_app = WebPy()
middleware = Middleware(web_app)

# Define a logging middleware handler
@middleware.register
def log_request_handler(request, response):
    """Log incoming request details."""
    print(f"[REQUEST] {request.method} {request.path}")
    if request.queries:  # Using queries instead of params
        print(f"[QUERY PARAMS] {request.queries}")
    # Can also log headers if needed
    print(f"[HEADERS] {request.headers}")

# Define a route with dynamic parameter <id:int>
@web_app.route("/user/<id:int>", methods=['GET'])
def get_user(request, response, id: int):
    # Respond with user information based on the provided ID
    response.headers['Content-Type'] = 'text/html'
    response.body = f"<html><body><h1>User ID: {id}</h1></body></html>".encode('utf-8')

# Define another route with a string parameter <slug:str>
@web_app.route("/post/<slug:str>", methods=['GET'])
@middleware.run()  # This will run all registered handlers (currently just log_request_handler)
def get_post(request, response, slug: str):
    # Respond with post information based on the provided slug
    response.headers['Content-Type'] = 'text/html'
    response.body = f"<html><body><h1>Post Slug: {slug}</h1></body></html>".encode('utf-8')

@web_app.error(404)
def custom_404_error_page(request, response) -> None:
    """Custom error handler for 404 Not Found."""
    response.headers['Content-Type'] = 'text/html'
    response.body = b"<html><body><h1>404 Not Found</h1><p>The page you're looking for doesn't exist.</p></body></html>"

# Define a simple static route
@web_app.route("/hello", methods=['GET'])
def hello(request, response):
    # Return a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello Page</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
    </html>
    """
    response.headers['Content-Type'] = 'text/html'
    response.body = html_content.encode('utf-8')

# Run the application
web_app.run()