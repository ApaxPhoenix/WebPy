from typing import Callable, List, Optional, Dict, Any, Type
from core import WebPyCore


class WebPy:
    """
    WebPy is a lightweight web application framework that uses WebPyCore for routing,
    error handling, template rendering, and server management.
    """

    def __init__(self) -> None:
        """Initialize WebPyCore as part of the WebPy app."""
        # Initialize the WebPyCore class as the core of the application
        self.app: Type[WebPyCore] = WebPyCore

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[Callable], Callable]:
        """
        Decorator to register routes for specific paths and HTTP methods.

        Args:
            path (str): URL path for the route (e.g., "/home").
            methods (Optional[List[str]]): HTTP methods allowed for this route. Defaults to ["GET"].

        Returns:
            Callable: A decorator that registers the handler function for the specified route.
        """
        # Default to GET method if no methods are provided
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            """
            Decorator function that registers the route with WebPyCore.
            Args:
                handler: The function to be executed when the route is accessed.
            Returns:
                The original handler function.
            """
            # Register the route with WebPyCore
            self.app.route(path, methods)(handler)
            return handler

        return decorator

    def error(self, code: int) -> Callable[[Callable], Callable]:
        """
        Decorator to register custom error handlers for specific HTTP status codes.

        Args:
            code (int): HTTP status code (e.g., 404 for Not Found, 500 for Internal Server Error).

        Returns:
            Callable: A decorator that registers the handler function for the specified error code.
        """

        def decorator(handler: Callable) -> Callable:
            """
            Decorator function to register an error handler with WebPyCore.
            Args:
                handler: The function to handle the error.
            Returns:
                The original handler function.
            """
            # Register the error handler with WebPyCore
            self.app.error(code)(handler)
            return handler

        return decorator

    def render(self, filename: str, **kwargs: Dict[str, Any]) -> str:
        """
        Renders an HTML template using WebPyCore's template environment.

        Args:
            filename (str): Filename of the template to render (e.g., "index.html").
            **kwargs: Key-value pairs representing variables to pass into the template.

        Returns:
            str: The rendered HTML content as a string.
        """
        # Use the template rendering engine from WebPyCore to render the specified template
        return self.app.render(filename, **kwargs)

    def run(self, ip: Optional[str] = "127.0.0.1", port: Optional[int] = 8080) -> None:
        """
        Start the web application server.

        Args:
            ip (Optional[str]): IP address to bind the server to. Defaults to '127.0.0.1'.
            port (Optional[int]): Port to listen on. Defaults to 8080.
        """
        # Start the web server with the specified IP and port, or use the defaults
        self.app.run(ip=ip, port=port)