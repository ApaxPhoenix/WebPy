from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader
from router import Router
from broadcast import Request, Response


class WebPyCore(BaseHTTPRequestHandler):
    """Core HTTP request handler with integrated routing, template rendering,
    static file serving, and customizable error handling for web applications."""

    # Jinja2 environment for rendering HTML templates
    template_env = Environment(loader=FileSystemLoader(Path("templates")))

    # Directory containing static files (CSS, JS, images, etc.)
    static_env = Path("static")

    # Mime types for commonly served files, mapped by file extensions
    mime_types: Dict[str, str] = {
        ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
        ".txt": "text/plain", ".json": "application/json", ".xml": "application/xml",
        ".pdf": "application/pdf", ".zip": "application/zip", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
        ".mp4": "video/mp4", ".webm": "video/webm", ".woff": "font/woff",
        ".woff2": "font/woff2", ".ttf": "font/ttf",
    }

    # Stores custom error handlers for specific HTTP status codes
    error_handlers: Dict[int, Callable[[Optional[Request], Response], None]] = {}

    def do_GET(self):
        self.serve_http_request("GET")

    def do_POST(self):
        self.serve_http_request("POST")

    def do_PUT(self):
        self.serve_http_request("PUT")

    def do_DELETE(self):
        self.serve_http_request("DELETE")

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable:
        """
        Decorator for registering HTTP routes with specific paths and methods.

        Args:
            path (str): URL path pattern to register for the route.
            methods (Optional[List[str]]): Allowed HTTP methods (e.g., GET, POST).

        Returns:
            Callable: The handler function decorated with routing capabilities.
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            Router.route(path, methods)(handler)
            return handler

        return decorator

    @classmethod
    def error(cls, code: int) -> Callable:
        """
        Decorator for assigning custom error handlers to HTTP status codes.

        Args:
            code (int): HTTP status code to handle (e.g., 404, 500).

        Returns:
            Callable: The error handler function registered for the specified code.
        """

        def decorator(handler: Callable) -> Callable:
            cls.error_handlers[code] = handler
            return handler

        return decorator

    def serve_http_request(self, method: str) -> None:
        """
        Processes incoming HTTP requests, either serving static files
        or routing requests based on URL and method.

        Args:
            method (str): The HTTP method (e.g., GET, POST) of the request.
        """
        try:
            request = Request(self)
            match = Router.match_route(request.path, method)

            if match:
                # Route match found: execute handler function with route parameters
                handler, params = match
                response = Response(self)
                handler(request, response, **params)
                response.send()
            elif request.path.startswith("/static/"):
                # Serve static files if the path is within the "static" directory
                self.serve_static_files(request.path)
            else:
                # Serve a 404 if no route or static file match is found
                self.serve(404, "Not Found")
        except Exception as error:
            # Handle internal errors (500) for exceptions
            self.serve(500, f"Internal Server Error: {str(error)}")

    def serve_static_files(self, path: str) -> None:
        """
        Serve static files (e.g., CSS, JS, images) with appropriate MIME types.

        Args:
            path (str): URL path to the static file.
        """
        relative_path = path[len("/static/"):]  # Remove "/static/" prefix
        try:
            file_path = Path(self.static_env, relative_path)
            with open(file_path, "rb") as file:
                # Respond with file content and correct MIME type
                self.send_response(200)
                # Retrieve the appropriate MIME type based on file extension.
                self.send_header("Content-type", self.mime_types.get(file_path.suffix.lower(), "application/octet-stream"))
                self.end_headers()
                self.wfile.write(file.read())
        except Exception as error:
            # Handle errors that occur when serving the static file
            self.serve(500, f"Internal Server Error: {str(error)}")

    @staticmethod
    def render(filename: str, **kwargs: Dict[str, Any]) -> str:
        """
        Renders an HTML template with given context data.

        Args:
            filename (str): Filename of the template to render.
            **kwargs: Key-value pairs representing variables for the template.

        Returns:
            str: Rendered HTML content.
        """
        template = WebPyCore.template_env.get_template(filename)
        return template.render(**kwargs)

    @classmethod
    def run(cls, ip: Optional[str] = None, port: Optional[int] = None,
            server_class: type = ThreadingHTTPServer, handler_class: Optional[type] = None) -> None:
        """
        Start the HTTP server, binding it to a specified IP and port.

        Args:
            ip (Optional[str]): IP address to bind (default: 127.0.0.1).
            port (Optional[int]): Port for the server (default: 8080).
            server_class (type): Server class, defaulting to ThreadingHTTPServer.
            handler_class (Optional[type]): Handler class for HTTP requests.
        """
        if handler_class is None:
            handler_class = cls
        try:
            server_address = (ip or "127.0.0.1", port or 8080)
            httpd = server_class(server_address, handler_class)
            print(f"Starting server on {server_address[0]}:{server_address[1]}")
            httpd.serve_forever()
        except OSError as error:
            print(f"Error starting server: {error}")

    def serve(self, code: int, message: str) -> None:
        """
        Handle error responses, leveraging custom error handlers if available.

        Args:
            code (int): HTTP status code (e.g., 404 for Not Found).
            message (str): Error message to display in the response.
        """
        if code in self.error_handlers:
            # Use registered custom error handler if available
            response = Response(self)
            handler = self.error_handlers[code]
            handler(None, response)  # Pass None for request in error cases
            response.send()
        else:
            # Default error response if no custom handler exists
            self.send_error(code, message)
