from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Type, Tuple, TypeVar, cast
from jinja2 import Environment, FileSystemLoader
from .router import Router
from .broadcast import Request, Response
import ssl
import warnings

# Enhanced type definitions for improved type safety and clarity
HandlerType = TypeVar("HandlerType", bound=Callable[[Request, Response, Any], None])
ErrorHandlerType = TypeVar("ErrorHandlerType", bound=Callable[[Optional[Request], Response], None])
RouteResult = Tuple[HandlerType, Dict[str, Any]]
GenericFunction = TypeVar("GenericFunction", bound=Callable)


class WebPyCore(BaseHTTPRequestHandler):
    """
    Comprehensive HTTP server framework with integrated routing, templating,
    and error handling capabilities.

    Provides a unified approach to web application development through:
    - Declarative routing with path parameters
    - Template-based rendering via Jinja2
    - Static file serving with MIME type detection
    - Custom error handling with fallbacks
    - Support for both HTTP and HTTPS connections

    This class serves as both the request handler and the application framework,
    allowing for a cohesive development experience with minimal boilerplate.
    """

    # Templating engine configuration with filesystem-based template loading
    template = Environment(loader=FileSystemLoader(Path("templates")))

    # Static file directory for serving assets like CSS, JavaScript and images
    static = Path("static")

    # Comprehensive MIME type mapping for content-type detection
    mimes: Dict[str, str] = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".txt": "text/plain",
        ".json": "application/json",
        ".xml": "application/xml",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".ttf": "font/ttf",
    }

    # Registry for custom error handlers mapped by status code
    errors: Dict[int, ErrorHandlerType] = {}

    def do_GET(self) -> None:
        """Process GET requests by delegating to the central request handler."""
        self.process("GET")

    def do_POST(self) -> None:
        """Process POST requests by delegating to the central request handler."""
        self.process("POST")

    def do_PUT(self) -> None:
        """Process PUT requests by delegating to the central request handler."""
        self.process("PUT")

    def do_DELETE(self) -> None:
        """Process DELETE requests by delegating to the central request handler."""
        self.process("DELETE")

    @classmethod
    def route(cls, pattern: str, methods: Optional[List[str]] = None) -> Callable[[GenericFunction], GenericFunction]:
        """
        Register route handlers for specific URL patterns and HTTP methods.

        Creates declarative routing through Python decorators, allowing
        for intuitive mapping between URL paths and handler functions.

        Parameters:
            pattern: URL pattern to match, supporting path parameters with syntax:
                    - Simple parameter: '<name>'
                    - Typed parameter: '<type:name>' (e.g., '<int:id>')
            methods: List of HTTP methods this route should handle (defaults to ["GET"])

        Returns:
            Decorator function that registers the handler with the routing system
        """
        if methods is None:
            methods = ["GET"]

        def decoration(handler: GenericFunction) -> GenericFunction:
            # Register handler with the Router using the specified pattern and methods
            Router.route(pattern, methods)(handler)
            return handler

        return decoration

    @classmethod
    def error(cls, status: int) -> Callable[[ErrorHandlerType], ErrorHandlerType]:
        """
        Register custom error handlers for specific HTTP status codes.

        Enables application-specific error pages and responses for better
        user experience and consistent error handling throughout the application.

        Parameters:
            status: HTTP status code to handle (e.g., 404, 500)

        Returns:
            Decorator function that registers the handler for the specified status code
        """

        def decoration(handler: ErrorHandlerType) -> ErrorHandlerType:
            # Store the handler in the error registry keyed by status code
            cls.errors[status] = handler
            return handler

        return decoration

    def process(self, method: str) -> None:
        """
        Central request processing pipeline for all HTTP methods.

        Handles the complete request lifecycle:
        1. Route matching based on request path and method
        2. Static file serving for assets under /static/
        3. Invoking the appropriate handler with extracted parameters
        4. Error handling for various failure scenarios

        Parameters:
            method: HTTP method of the current request (GET, POST, etc.)
        """
        try:
            # Create request object from raw HTTP request
            request: Request = Request(self)

            # Attempt to match the request against registered routes
            matching: Optional[RouteResult] = Router.match(request.path, method)

            if matching:
                # Execute matched handler with extracted path parameters
                handler, parameters = cast(RouteResult, matching)
                response: Response = Response(self)
                handler(request, response, **parameters)
                response.send()
            elif request.path.startswith("/static/"):
                # Handle static file requests with dedicated method
                self.deliver(request.path)
            else:
                # No route matched and not a static file - return 404
                self.warn(404, "Not Found")
        except Exception as exception:
            # Catch and handle any unhandled exceptions as 500 errors
            self.warn(500, f"Internal Server Error: {str(exception)}")

    def deliver(self, filepath: str) -> None:
        """
        Serve static files with appropriate MIME type detection.

        Handles delivery of files from the static directory with proper content
        types determined by file extension, supporting a wide range of asset types.

        Parameters:
            filepath: Request path to the static file (starting with "/static/")
        """
        try:
            # Extract relative path by removing the "/static/" prefix
            resource: Path = Path(self.static, filepath[len("/static/"):])

            # Read file content as binary data
            with open(resource, "rb") as filedata:
                # Send successful response with appropriate MIME type
                self.send_response(200)
                self.send_header(
                    "Content-type",
                    self.mimes.get(resource.suffix.lower(), "application/octet-stream"),
                )
                self.end_headers()
                self.wfile.write(filedata.read())
        except FileNotFoundError:
            # File doesn't exist in static directory
            self.warn(404, "File Not Found")
        except Exception as exception:
            # Handle other file access errors (permissions, etc.)
            warnings.warn(f"Error serving static file {filepath}: {exception}")
            self.warn(500, "Internal Server Error")

    @staticmethod
    def render(template_name: str, **context: Any) -> str:
        """
        Render HTML templates with Jinja2 templating engine.

        Provides powerful templating capabilities for generating dynamic HTML
        content with context variables, template inheritance, and more.

        Parameters:
            template_name: Name of the template file to render
            **context: Template variables to inject into the rendering context

        Returns:
            Rendered HTML content as a string

        Example:
            response.html(WebPyCore.render('user_profile.html', user=user, editable=True))
        """
        # Load the template by name and render with provided context
        template = WebPyCore.template.get_template(template_name)
        return template.render(**context)

    @classmethod
    def run(
            cls,
            ip: str = "127.0.0.1",
            port: int = 8080,
            server: Type[ThreadingHTTPServer] = ThreadingHTTPServer,
            handler: Optional[Type[BaseHTTPRequestHandler]] = None,
            certfile: Optional[str] = None,
            keyfile: Optional[str] = None,
    ) -> None:
        """
        Start the web application server with optional HTTPS support.

        This method initializes and runs the HTTP/HTTPS server, binding it to the specified
        IP address and port. It supports both HTTP and HTTPS protocols, with HTTPS enabled
        when both `certfile` and `keyfile` are provided.

        Parameters:
            ip: IP address to bind the server to (default: "127.0.0.1").
            port: TCP port to listen on (default: 8080).
            server: The server class to use (default: `ThreadingHTTPServer`).
            handler: The request handler class to use. If not provided, defaults to `WebPyCore`.
            certfile: Path to the SSL certificate file for HTTPS (optional).
            keyfile: Path to the SSL private key file for HTTPS (optional).

        Raises:
            OSError: If the server cannot bind to the specified IP and port.

        Note:
            To enable HTTPS, both `certfile` and `keyfile` must be provided. If only one is
            provided, a warning will be issued, and the server will fall back to HTTP.
        """
        if handler is None:
            handler = cls

        # Initialize the server with the specified IP, port, and handler
        instance = server((ip, port), handler)

        # Validate SSL configuration (both certfile and keyfile are required for HTTPS)
        if bool(certfile) != bool(keyfile):
            warnings.warn(
                "Both certfile and keyfile are required for HTTPS to work.", UserWarning
            )
        elif certfile and keyfile:
            # Configure HTTPS if both certfile and keyfile are provided
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            instance.socket = context.wrap_socket(instance.socket, server_side=True)
            print(f"Starting HTTPS server on {ip}:{port}")
        else:
            # Fall back to HTTP if SSL files are not provided
            print(f"Starting HTTP server on {ip}:{port}")

        try:
            # Run the server indefinitely
            instance.serve_forever()
        except OSError as exception:
            warnings.warn(f"Error starting server: {exception}")
            raise

    def warn(self, status: int, message: str) -> None:
        """
        Process HTTP errors with custom handlers when available.

        Provides consistent error handling throughout the application,
        with support for customized error pages through registered handlers.

        Parameters:
            status: HTTP status code for the error response
            message: Human-readable error message
        """
        if status in self.errors:
            # Use registered custom error handler if available
            response = Response(self)
            handler = self.errors[status]
            handler(None, response)  # No request object in error context
            response.send()
        else:
            # Fall back to default error handling
            self.send_error(status, message)