from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader
from .router import Router
from .broadcast import Request, Response

class WebPyCore(BaseHTTPRequestHandler):
    """HTTP request handler with template rendering and static file serving."""

    # Jinja2 environment for rendering templates from the 'templates' directory
    template_env = Environment(loader=FileSystemLoader(Path("templates")))

    # Directory for static files like CSS, JS, images, etc.
    static_env = Path("static")

    # MIME type mapping for various file extensions
    MIME_TYPES: Dict[str, str] = {
        # Text-based content types
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".txt": "text/plain",
        # Application-based content types
        ".json": "application/json",
        ".xml": "application/xml",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        # Image content types
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        # Audio and video content types
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        # Font content types
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
    }

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable:
        """
        Decorator to register routes.

        Args:
            path (str): URL path for the route.
            methods (Optional[List[str]]): List of HTTP methods allowed for this route.

        Returns:
            Callable: Decorated handler function.
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            # Register the route with the Router
            Router.route(path, methods)(handler)
            return handler
        return decorator

    def do_GET(self) -> None:
        """Handle HTTP GET requests."""
        self.handle_request("GET")

    def do_POST(self) -> None:
        """Handle HTTP POST requests."""
        self.handle_request("POST")

    def do_PUT(self) -> None:
        """Handle HTTP PUT requests."""
        self.handle_request("PUT")

    def do_DELETE(self) -> None:
        """Handle HTTP DELETE requests."""
        self.handle_request("DELETE")

    def handle_request(self, method: str) -> None:
        """
        Handle HTTP requests by delegating to route-specific handlers.

        Args:
            method (str): HTTP method of the request.
        """
        try:
            # Create a Request object from the current handler
            request = Request(self)
            # Route the request based on the HTTP method and path
            self.handle_route_request(method, request)
        except Exception as error:
            # Send a 500 Internal Server Error response on exception
            self.send_error(500, f"Internal Server Error: {str(error)}")

    def handle_route_request(self, method: str, request: Request) -> None:
        """
        Handle requests for registered routes.

        Args:
            method (str): HTTP method of the request.
            request (Request): Request object.
        """
        try:
            # Get route information based on the request path
            handler_info = Router.get_route(request.path)
            if handler_info:
                # Check if the method is allowed for this route
                allowed_methods = Router.get_allowed_methods(request.path)
                if method in allowed_methods:
                    handler = handler_info["handler"]
                    # Create a Response object to send back to the client
                    response = Response(self)
                    # Call the route handler with the request and response
                    handler(request, response)
                    # Send the response to the client
                    response.send()
                else:
                    # Send a 405 Method Not Allowed response
                    self.send_error(405, f"Method {method} not allowed")
            elif request.path.startswith("/static/"):
                # Serve static files from the 'static' directory
                self.serve_static_file(request.path)
            else:
                # Send a 404 Not Found response if no route matches
                self.send_error(404, "Not Found")
        except Exception as error:
            # Send a 500 Internal Server Error response on exception
            self.send_error(500, f"Internal Server Error: {str(error)}")

    def serve_static_file(self, path: str) -> None:
        """
        Serve static files with appropriate MIME types.

        Args:
            path (str): Path to the static file.
        """
        relative_path = path[len("/static/"):]  # Strip '/static/' prefix
        try:
            # Construct the file path from the static directory
            file_path = Path(self.static_env, relative_path)
            with open(file_path, "rb") as file:
                self.send_response(200)  # Send HTTP 200 OK status
                content_type = self.get_mime_type(file_path)  # Determine MIME type
                self.send_header("Content-type", content_type)
                self.end_headers()
                # Write the file content to the response
                self.wfile.write(file.read())
        except FileNotFoundError:
            # Send a 404 Not Found response if the file does not exist
            self.send_error(404)

    @classmethod
    def get_mime_type(cls, file_path: Path) -> str:
        """
        Get the MIME type for a given file based on its extension.

        Args:
            file_path (Path): Path object of the file.

        Returns:
            str: MIME type string.
        """
        # Return the MIME type from the mapping, or default to 'application/octet-stream'
        return cls.MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")

    def render_template(self, template_name: str, **kwargs: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with given context.

        Args:
            template_name (str): Name of the template file.
            **kwargs: Variables to pass to the template.

        Returns:
            str: Rendered template as a string.
        """
        # Load and render the template with provided context
        template = self.template_env.get_template(template_name)
        return template.render(**kwargs)

    @classmethod
    def run(cls, ip: Optional[str] = None, port: Optional[int] = None, 
            server_class: type = ThreadingHTTPServer, handler_class: Optional[type] = None) -> None:
        """
        Start the web server.

        Args:
            ip (Optional[str]): IP address to bind to.
            port (Optional[int]): Port number to listen on.
            server_class (type): Class to use for the HTTP server.
            handler_class (Optional[type]): Class to use for handling requests.
        """
        if handler_class is None:
            handler_class = cls
        try:
            # Define the server address and port
            server_address = (ip or "127.0.0.1", port or 8080)
            # Create and start the server
            httpd = server_class(server_address, handler_class)
            print(f"Starting server on {server_address[0]}:{server_address[1]}")
            httpd.serve_forever()
        except OSError as error:
            # Print error if the server fails to start
            print(f"Error starting server: {error}")
