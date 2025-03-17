from typing import List, Callable, Any, TypeVar, Dict
from functools import wraps
from pathlib import Path

# Type variable for generic function type annotation
T = TypeVar('T', bound=Callable[..., Any])


class Blueprint:
    """Blueprint for organizing routes into modular components within a web application."""

    def __init__(self, name: str, prefix: str) -> None:
        """
        Initialize a blueprint with a name and optional URL prefix.

        Args:
            name: Unique identifier for the blueprint
            prefix: URL prefix for all routes in this blueprint (defaults to empty string)
        """
        self.name = name
        # Normalize the prefix using pathlib
        self.prefix = Path('/', prefix.lstrip('/'))
        self.routes: Dict[str, Dict[str, Any]] = {}

    def route(self, path: str, methods: List[str] = None) -> Callable[[T], T]:
        """
        Register a route handler for a specific path and HTTP methods.

        Args:
            path: URL path pattern (will be prefixed with blueprint prefix)
            methods: List of HTTP methods (defaults to ["GET"])

        Returns:
            Decorator function that registers the handler function
        """
        methods = methods or ["GET"]

        def decorator(handler: T) -> T:
            # Normalize and join paths using pathlib
            endpoint = Path(self.prefix, path.lstrip('/'))

            # Ensure the route path starts with a slash
            if not str(endpoint).startswith('/'):
                endpoint = Path('/', endpoint)

            # Store the route configuration
            self.routes[str(endpoint)] = {
                "handler": handler,
                "methods": methods
            }
            return handler

        return decorator

    def register(self, app: Any) -> None:
        """
        Register all blueprint routes with the main application.

        Args:
            app: The web application instance to register routes with
                 (typically a WebPy application instance)

        Note:
            This method is typically called by the WebPy.blueprint() method
            rather than directly by users.
        """
        # Register each blueprint route with the main application
        for path, config in self.routes.items():
            handler = config["handler"]
            methods = config["methods"]

            # Create a wrapper that preserves the original function's metadata
            @app.route(path, methods=methods)
            @wraps(handler)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return handler(*args, **kwargs)