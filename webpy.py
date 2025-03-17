from typing import Callable, List, Optional, Any, Type, TypeVar
from .core import WebPyCore

# Type variables for better function typing
T = TypeVar('T', bound=Callable[..., Any])
RouteHandler = Callable[..., Any]
ErrorHandler = Callable[..., Any]


class WebPy:
    """
    Main WebPy framework class that provides a simplified interface to WebPyCore.

    This class serves as the primary API for creating web applications with WebPy,
    offering convenient methods for routing, error handling, template rendering,
    and server initialization.
    """

    def __init__(self) -> None:
        """
        Initialize a new WebPy application instance.

        Sets up a reference to the WebPyCore class which handles the underlying
        HTTP server implementation.
        """
        self.app: Type[WebPyCore] = WebPyCore

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[T], T]:
        """
        Decorator to register route handlers for specific URL paths and HTTP methods.

        This method provides a convenient interface to the underlying routing system,
        allowing route handlers to be defined with a simple decorator syntax.

        Args:
            path (str): URL path pattern for the route (can include dynamic segments).
            methods (Optional[List[str]]): List of HTTP methods allowed for this route.
                                          Defaults to ["GET"] if not specified.

        Returns:
            Callable[[T], T]: A decorator that registers the handler function with the routing system.

        Example:
            @app.route("/users/<id:int>", methods=["GET", "POST"])
            def user_handler(request, response, id):
                # Handle user requests
                pass
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: T) -> T:
            """
            Inner decorator function that registers the route handler with WebPyCore.

            Args:
                handler (T): The function that will handle requests to this route.

            Returns:
                T: The original handler function, unchanged.
            """
            self.app.route(path, methods)(handler)
            return handler

        return decorator

    def error(self, code: int) -> Callable[[ErrorHandler], ErrorHandler]:
        """
        Decorator to register custom error handlers for specific HTTP status codes.

        This allows for customized error pages or API responses when specific
        HTTP errors occur (e.g., 404 Not Found, 500 Internal Server Error).

        Args:
            code (int): HTTP status code to handle (e.g., 404, 500).

        Returns:
            Callable[[ErrorHandler], ErrorHandler]: A decorator that registers the error handler function.

        Example:
            @app.error(404)
            def not_found(request, response):
                response.status = 404
                return response.json({"error": "Resource not found"})
        """

        def decorator(handler: ErrorHandler) -> ErrorHandler:
            """
            Inner decorator function that registers the error handler with WebPyCore.

            Args:
                handler (ErrorHandler): The function that will handle the specific error.

            Returns:
                ErrorHandler: The original handler function, unchanged.
            """
            self.app.error(code)(handler)
            return handler

        return decorator

    def render(self, filename: str, **kwargs: Any) -> str:
        """
        Renders an HTML template using the WebPyCore's template environment.

        This method provides a simplified interface to the Jinja2 template engine
        integrated with WebPyCore.

        Args:
            filename (str): Filename of the template to render (must be in the templates directory).
            **kwargs: Key-value pairs representing variables to be used in the template context.

        Returns:
            str: The rendered HTML content as a string.

        Example:
            html = app.render("profile.html", user=user_data, active_page="profile")
        """
        return self.app.render(filename, **kwargs)

    def run(self, ip: str = "127.0.0.1", port: int = 8080,
            certfile: Optional[str] = None, keyfile: Optional[str] = None) -> None:
        """
        Start the web application server.

        This method initializes and runs the HTTP/HTTPS server with the configured
        routes and settings.

        Args:
            ip (str): IP address to bind the server to. Defaults to '127.0.0.1' (localhost).
            port (int): Port number to listen on. Defaults to 8080.
            certfile (Optional[str]): Path to the SSL certificate file for HTTPS support.
                                    Required together with keyfile for HTTPS.
            keyfile (Optional[str]): Path to the SSL key file for HTTPS support.
                                   Required together with certfile for HTTPS.

        Note:
            If both certfile and keyfile are provided, the server will use HTTPS.
            Otherwise, it will use standard HTTP.
        """
        self.app.run(ip=ip, port=port, certfile=certfile, keyfile=keyfile)