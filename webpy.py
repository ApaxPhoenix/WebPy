from typing import Callable, List, Optional, Dict, Any, Type
from core import WebPyCore


class WebPy:
    def __init__(self) -> None:
        """Initialize WebPyCore as part of the WebPy app."""
        self.app: Type[WebPyCore] = WebPyCore

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[Callable], Callable]:
        """
        Decorator to register routes for specific paths and methods.

        Args:
            path (str): URL path for the route.
            methods (Optional[List[str]]): HTTP methods allowed for this route. Defaults to ["GET"].

        Returns:
            Callable: Decorated handler function.
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            """Registers the route with WebPyCore."""
            self.app.route(path, methods)(handler)
            return handler

        return decorator

    def error(self, code: int) -> Callable[[Callable], Callable]:
        """
        Decorator to register custom error handlers for specific HTTP status codes.

        Args:
            code (int): HTTP status code (e.g., 404, 500) to handle.

        Returns:
            Callable: Decorated error handler function.
        """
        def decorator(handler: Callable) -> Callable:
            """Registers the error handler with WebPyCore."""
            self.app.error(code)(handler)
            return handler

        return decorator

    def render(self, filename: str, **kwargs: Dict[str, Any]) -> str:
        """
        Renders an HTML template using the WebPyCore's template environment.

        Args:
            filename (str): Filename of the template to render.
            **kwargs: Key-value pairs representing variables for the template.

        Returns:
            str: Rendered HTML content.
        """
        return self.app.render(filename, **kwargs)

    def run(self, ip: Optional[str] = "127.0.0.1", port: Optional[int] = 8080,
            certfile: Optional[str] = None, keyfile: Optional[str] = None) -> None:
        """
        Start the web application server.

        Args:
            ip (str, optional): IP address to bind the server to. Defaults to '127.0.0.1'.
            port (int, optional): Port to listen on. Defaults to 8080.
            certfile (Optional[str]): Path to the SSL certificate file.
            keyfile (Optional[str]): Path to the SSL key file.
        """
        self.app.run(ip=ip, port=port, certfile=certfile, keyfile=keyfile)
