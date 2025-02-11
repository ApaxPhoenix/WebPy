from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Type
from jinja2 import Environment, FileSystemLoader
from .router import Router
from .broadcast import Request, Response
import ssl
import warnings


class WebPyCore(BaseHTTPRequestHandler):
    """
    Core HTTP request handler with integrated routing, template rendering,
    static file serving, and customizable error handling for web applications.
    """

    # Jinja2 environment for rendering HTML templates from the "templates" directory
    template_env = Environment(loader=FileSystemLoader(Path("templates")))

    # Directory containing static files (e.g., CSS, JS, images)
    static_env = Path("static")

    # MIME types for commonly served files, mapped by file extensions
    mimes: Dict[str, str] = {
        ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
        ".txt": "text/plain", ".json": "application/json", ".xml": "application/xml",
        ".pdf": "application/pdf", ".zip": "application/zip", ".png": "image/png",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
        ".svg": "image/svg+xml", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
        ".mp4": "video/mp4", ".webm": "video/webm", ".woff": "font/woff",
        ".woff2": "font/woff2", ".ttf": "font/ttf",
    }

    # Stores custom error handlers for specific HTTP status codes
    errors: Dict[int, Callable[[Optional[Request], Response], None]] = {}

    def do_GET(self):
        """Handle HTTP GET requests by calling the generic serve_http_request method."""
        self.serve_http_request("GET")

    def do_POST(self):
        """Handle HTTP POST requests by calling the generic serve_http_request method."""
        self.serve_http_request("POST")

    def do_PUT(self):
        """Handle HTTP PUT requests by calling the generic serve_http_request method."""
        self.serve_http_request("PUT")

    def do_DELETE(self):
        """Handle HTTP DELETE requests by calling the generic serve_http_request method."""
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
            # Register the handler with the Router for the specified path and methods
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
            # Register the handler for a specific HTTP error code
            cls.errors[code] = handler
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
            # Create Request and match it against registered routes
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
        # Strip "/static/" from path to get relative file path
        relative_path = path[len("/static/"):]
        try:
            file_path = Path(self.static_env, relative_path)
            with open(file_path, "rb") as file:
                # Send response with file content and correct MIME type
                self.send_response(200)
                self.send_header("Content-type", self.mimes.get(file_path.suffix.lower(), "application/octet-stream"))
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.serve(404, "File Not Found")
        except Exception as error:
            warnings.warn(f"Error serving static file {path}: {error}")
            self.serve(500, "Internal Server Error")

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
        # Load and render the specified template with provided context
        template = WebPyCore.template_env.get_template(filename)
        return template.render(**kwargs)

    @classmethod
    def run(cls, ip: str = '127.0.0.1', port: int = 8080,
            server: Type[ThreadingHTTPServer] = ThreadingHTTPServer,
            handler: Optional[Type] = None,
            certfile: Optional[str] = None, keyfile: Optional[str] = None) -> None:
        """
        Start the server, with optional HTTPS if both certfile and keyfile are provided.

        Args:
            ip (str): IP address to bind (default: 127.0.0.1).
            port (int): Port for the server (default: 8080).
            server (type): Server class, defaulting to ThreadingHTTPServer.
            handler (Optional[type]): Handler class for HTTP requests.
            certfile (Optional[str]): Path to the SSL certificate file.
            keyfile (Optional[str]): Path to the SSL key file.
        """
        if handler is None:
            handler = cls

        # Initialize server with the specified handler
        host = server((ip, port), handler)

        # Warn and exit if only one of certfile or keyfile is provided
        if (certfile and not keyfile) or (keyfile and not certfile):
            warnings.warn("Both certfile and keyfile are required for HTTPS to work.", UserWarning)
            return

        # Setup SSL context if both certfile and keyfile are provided
        if certfile and keyfile:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            host.socket = context.wrap_socket(host.socket, server_side=True)
            print(f"Starting HTTPS server on {ip}:{port}")
        else:
            print(f"Starting HTTP server on {ip}:{port}")

        try:
            host.serve_forever()
        except OSError as error:
            warnings.warn(f"Error starting server: {error}")
            raise

    def serve(self, code: int, message: str) -> None:
        """
        Handle error responses, leveraging custom error handlers if available.

        Args:
            code (int): HTTP status code (e.g., 404 for Not Found).
            message (str): Error message to display in the response.
        """
        if code in self.errors:
            # Use registered custom error handler if available
            response = Response(self)
            handler = self.errors[code]
            handler(None, response)  # Pass None for request in error cases
            response.send()
        else:
            # Default error response if no custom handler exists
            self.send_error(code, message)
