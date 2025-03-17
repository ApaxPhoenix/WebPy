from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Type, Tuple, TypeVar, cast
from jinja2 import Environment, FileSystemLoader
from .router import Router
from .broadcast import Request, Response
from .blueprint import Blueprint
import ssl
import warnings

# Type definitions for better clarity
HandlerFunction = Callable[[Request, Response, Any], None]
ErrorHandlerFunction = Callable[[Optional[Request], Response], None]
RouteMatchResult = Tuple[HandlerFunction, Dict[str, Any]]
T = TypeVar('T', bound=Callable)


class WebPyCore(BaseHTTPRequestHandler):
    """
    Core HTTP request handler with integrated routing, template rendering,
    static file serving, and customizable error handling for web applications.

    This class extends BaseHTTPRequestHandler to provide a complete framework
    for building web applications with clean separation of concerns.
    """

    # Jinja2 environment for rendering HTML templates from the "templates" directory
    template = Environment(loader=FileSystemLoader(Path("templates")))

    # Directory containing static files (e.g., CSS, JS, images)
    static = Path("static")

    # MIME types for commonly served files, mapped by file extensions
    # Used to set appropriate Content-Type headers when serving static files
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
    # Keys are HTTP status codes, values are handler functions
    errors: Dict[int, ErrorHandlerFunction] = {}

    def do_GET(self) -> None:
        """Handle HTTP GET requests by calling the generic serve method."""
        self.serve("GET")

    def do_POST(self) -> None:
        """Handle HTTP POST requests by calling the generic serve method."""
        self.serve("POST")

    def do_PUT(self) -> None:
        """Handle HTTP PUT requests by calling the generic serve method."""
        self.serve("PUT")

    def do_DELETE(self) -> None:
        """Handle HTTP DELETE requests by calling the generic serve method."""
        self.serve("DELETE")

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable[[T], T]:
        """
        Decorator for registering HTTP routes with specific paths and methods.

        Creates a mapping between URL paths and handler functions, allowing
        automatic request routing based on the requested path and HTTP method.

        Args:
            path (str): URL path pattern to register for the route (can include parameters).
            methods (Optional[List[str]]): Allowed HTTP methods for this route (e.g., ["GET", "POST"]).
                                          Defaults to ["GET"] if not specified.

        Returns:
            Callable: Decorator function that registers the handler with the Router.

        Example:
            @WebPyCore.route("/users/:id", methods=["GET"])
            def get_user(request, response, id):
                # Handle user retrieval by ID
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: T) -> T:
            # Register the handler with the Router for the specified path and methods
            Router.route(path, methods)(handler)
            return handler

        return decorator

    @classmethod
    def error(cls, code: int) -> Callable[[ErrorHandlerFunction], ErrorHandlerFunction]:
        """
        Decorator for assigning custom error handlers to HTTP status codes.

        Allows custom handling of specific HTTP error codes, providing better
        user experience than default error pages.

        Args:
            code (int): HTTP status code to handle (e.g., 404, 500).

        Returns:
            Callable: Decorator that registers the error handler function.

        Example:
            @WebPyCore.error(404)
            def not_found(request, response):
                response.status(404).html("<h1>Page not found</h1>")
        """

        def decorator(handler: ErrorHandlerFunction) -> ErrorHandlerFunction:
            # Register the handler for a specific HTTP error code
            cls.errors[code] = handler
            return handler

        return decorator

    def serve(self, method: str) -> None:
        """
        Processes incoming HTTP requests, either serving static files
        or routing requests based on URL and method.

        This is the central dispatch method that handles all incoming requests
        by finding the appropriate handler or serving static files.

        Args:
            method (str): The HTTP method (e.g., GET, POST) of the request.
        """
        try:
            # Create Request object and match it against registered routes
            request = Request(self)
            match = Router.match(request.path, method)

            if match:
                # Route match found: execute handler function with extracted route parameters
                handler, params = cast(RouteMatchResult, match)
                response = Response(self)
                handler(request, response, **params)
                response.send()
            elif request.path.startswith("/static/"):
                # Serve static files if the path is within the "static" directory
                self.link(request.path)
            else:
                # Return a 404 if no route or static file match is found
                self.warn(404, "Not Found")
        except Exception as error:
            # Handle internal errors (500) for all uncaught exceptions
            self.warn(500, f"Internal Server Error: {str(error)}")

    def link(self, path: str) -> None:
        """
        Serve static files (e.g., CSS, JS, images) with appropriate MIME types.

        Handles delivery of files from the static directory with proper content types
        based on file extensions.

        Args:
            path (str): URL path to the static file (starting with "/static/").
        """
        try:
            # Remove the "/static/" prefix to get the relative path
            filepath = Path(self.static, path[len("/static/"):])
            with open(filepath, "rb") as file:
                # Send response with file content and correct MIME type
                self.send_response(200)
                self.send_header("Content-type", self.mimes.get(filepath.suffix.lower(), "application/octet-stream"))
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.warn(404, "File Not Found")
        except Exception as error:
            warnings.warn(f"Error serving static file {path}: {error}")
            self.warn(500, "Internal Server Error")

    @staticmethod
    def render(filename: str, **kwargs: Any) -> str:
        """
        Renders an HTML template with given context data using Jinja2.

        Provides templating capabilities for generating dynamic HTML content.

        Args:
            filename (str): Filename of the template to render (must be in the templates directory).
            **kwargs: Key-value pairs representing variables for the template context.

        Returns:
            str: Rendered HTML content as a string.

        Example:
            html_content = WebPyCore.render("user_profile.html", user=user_data)
        """
        # Load and render the specified template with provided context
        template = WebPyCore.template.get_template(filename)
        return template.render(**kwargs)

    def blueprint(self, blueprint: Blueprint) -> None:
        """
        Register a blueprint with the application.

        This method adds all routes defined in the blueprint to the application,
        respecting the blueprint's prefix.

        Args:
            blueprint (Blueprint): The blueprint instance to register.

        Example:
            # Create a blueprint
            user_bp = Blueprint('user', prefix='/user')

            # Define routes on the blueprint
            @user_bp.route('/profile')
            def profile(request, response):
                pass

            # Register the blueprint with the application
            app.blueprint(user_bp)
        """
        # Call the blueprint's register method to register all routes
        blueprint.register(self)

    @classmethod
    def run(cls, ip: str = '127.0.0.1', port: int = 8080,
            server: Type[ThreadingHTTPServer] = ThreadingHTTPServer,
            handler: Optional[Type[BaseHTTPRequestHandler], Any] = None,
            certfile: Optional[str] = None, keyfile: Optional[str] = None) -> None:
        """
        Start the web server, with optional HTTPS if both certfile and keyfile are provided.

        This is the main entry point for running the web application server.

        Args:
            ip (str): IP address to bind (default: 127.0.0.1 for localhost only).
            port (int): Port for the server to listen on (default: 8080).
            server (Type[ThreadingHTTPServer]): Server class, defaulting to ThreadingHTTPServer.
            handler (Optional[Type[BaseHTTPRequestHandler]]): Handler class for HTTP requests.
            certfile (Optional[str]): Path to the SSL certificate file for HTTPS.
            keyfile (Optional[str]): Path to the SSL key file for HTTPS.

        Raises:
            OSError: If the server cannot be started (e.g., port already in use).
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
            # Start the server and keep it running until interrupted
            host.serve_forever()
        except OSError as error:
            warnings.warn(f"Error starting server: {error}")
            raise

    def warn(self, code: int, message: str) -> None:
        """
        Handle error responses, leveraging custom error handlers if available.

        Provides consistent error handling throughout the application, with
        support for custom error pages when registered.

        Args:
            code (int): HTTP status code (e.g., 404 for Not Found, 500 for Server Error).
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