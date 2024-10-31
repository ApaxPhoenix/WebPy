import re
from typing import Callable, Dict, List, Optional, Union, Tuple, Pattern


class Router:
    """
    A simple router class that registers routes and matches them based on
    path and HTTP method using regular expressions.

    Attributes:
        routes (Dict[str, Dict[str, Union[Callable, List[str], Pattern]]]):
            A dictionary to store routes, handlers, allowed methods, and compiled regex patterns.
    """
    routes: Dict[str, Dict[str, Union[Callable, List[str], Pattern]]] = {}

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable[[Callable], Callable]:
        """
        Decorator to register a route with an optional list of HTTP methods.

        Args:
            path (str): The route path, potentially including dynamic segments (e.g., "/user/<id:int>").
            methods (Optional[List[str]]): The list of allowed HTTP methods for the route. Defaults to ["GET"].

        Returns:
            Callable[[Callable], Callable]: A decorator function that registers the handler for the route.
        """
        if methods is None:
            methods = ["GET"]

        # Convert dynamic path segments to regex patterns for parameter extraction
        pattern = re.sub(r"<(\w+):(\w+)>", r"(?P<\1>[^/]+)", path)
        regex: Pattern = re.compile(f"^{pattern}$")

        def decorator(handler: Callable) -> Callable:
            """
            Registers the route by associating the path with the handler,
            allowed methods, and compiled regex pattern.

            Args:
                handler (Callable): The function that handles requests to the route.

            Returns:
                Callable: The original handler function.
            """
            # Store the route details: handler, allowed methods, and compiled regex pattern
            cls.routes[path] = {
                "handler": handler,
                "methods": methods,
                "pattern": regex
            }
            return handler

        return decorator

    @classmethod
    def match_route(cls, path: str, method: str) -> Optional[Tuple[Callable, Dict[str, str]]]:
        """
        Match the incoming request path and method to a registered route.

        Args:
            path (str): The request path.
            method (str): The HTTP method of the request (e.g., "GET", "POST").

        Returns:
            Optional[Tuple[Callable, Dict[str, str]]]:
                If a match is found, returns a tuple of the route handler and a dictionary of extracted parameters.
                If no match is found, returns None.
        """
        # Iterate over all registered routes to find a matching path and method
        for route in cls.routes.values():
            pattern: Pattern = route.get("pattern")
            allowed_methods = route.get("methods", ["GET"])

            # Check if the route pattern matches the path and method is allowed
            if pattern and pattern.match(path) and method in allowed_methods:
                handler = route["handler"]
                match = pattern.match(path)
                params = match.groupdict() if match else {}
                return handler, params  # Return the matched handler and extracted parameters

        return None  # Return None if no match is found

    @classmethod
    def get_allowed_methods(cls, path: str) -> List[str]:
        """
        Get a list of allowed HTTP methods for a given path.

        Args:
            path (str): The route path.

        Returns:
            List[str]: A list of allowed methods for the route, or ["GET"] if no specific methods are registered.
        """
        # Iterate over the registered routes to check if the path matches any pattern
        for route in cls.routes.values():
            pattern: Pattern = route.get("pattern")
            if pattern and pattern.match(path):
                return route.get("methods", ["GET"])  # Return the allowed methods for the route

        return ["GET"]  # Default to "GET" if no match is found
