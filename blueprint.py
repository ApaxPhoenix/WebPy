from typing import Dict, List, Optional, Callable, Any, TypeVar
from functools import wraps

# Type variables for better function typing
T = TypeVar('T', bound=Callable[..., Any])
RouteHandler = Callable[..., Any]


class Blueprint:
    """
    Blueprint class for organizing routes into modular components.

    Blueprints allow for grouping related routes under a common URL prefix,
    enabling better organization of large applications by splitting them into
    smaller, self-contained components that can be registered with the main
    application.
    """

    def __init__(self, name: str, prefix: str = None) -> None:
        """
        Initialize a new Blueprint instance.

        Creates a blueprint with a unique name and optional URL prefix that will
        be prepended to all routes registered with this blueprint.

        Args:
            name (str): Unique identifier for the blueprint. Used for registration
                       and debugging purposes.
            prefix (str): URL prefix to prepend to all routes in this blueprint.
                         Defaults to an empty string (no prefix).
        """
        self.name = name
        self.prefix = prefix
        # Store routes as a dictionary mapping paths to handlers and methods
        self.routes: Dict[str, Dict[str, Any]] = {}

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[T], T]:
        """
        Decorator to register route handlers for specific URL paths and HTTP methods.

        This method works similarly to WebPy's route decorator but registers
        routes within the blueprint's namespace.

        Args:
            path (str): URL path pattern for the route (can include dynamic segments).
                       This will be prefixed with the blueprint's prefix.
            methods (Optional[List[str]]): List of HTTP methods allowed for this route.
                                          Defaults to ["GET"] if not specified.

        Returns:
            Callable[[T], T]: A decorator that registers the handler function
                             with the blueprint's routing system.

        Example:
            @user_blueprint.route("/profile/<id:int>", methods=["GET", "POST"])
            def user_profile(request, response, id):
                # Handle user profile requests
                pass
        """
        if methods is None:
            methods = ["GET"]

        # Normalize the path to ensure it starts with a slash
        if not path.startswith("/"):
            path = f"/{path}"

        # Create the full path by combining the blueprint prefix with the route path
        full_path = f"{self.prefix}{path}"

        def decorator(handler: T) -> T:
            """
            Inner decorator function that registers the route handler with the blueprint.

            Args:
                handler (T): The function that will handle requests to this route.

            Returns:
                T: The original handler function, unchanged.
            """
            # Store the route configuration in the blueprint's routes dictionary
            self.routes[full_path] = {
                "handler": handler,
                "methods": methods
            }
            return handler

        return decorator

    def register(self, app: Any) -> None:
        """
        Register all routes defined in this blueprint with the main application.

        This method is typically called by the WebPy.blueprint() method rather
        than directly by users.

        Args:
            app (Any): The WebPy application instance to register routes with.
        """
        # Iterate through all routes registered with this blueprint
        for path, config in self.routes.items():
            handler = config["handler"]
            methods = config["methods"]

            # Register each route with the main application
            @app.route(path, methods=methods)
            @wraps(handler)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return handler(*args, **kwargs)