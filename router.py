import re
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
    Tuple,
    Pattern,
    TypeVar,
    Any,
    cast,
)

# Define type variables and type aliases for better type hinting
T = TypeVar("T", bound=Callable[..., Any])
RouteHandler = Callable[..., Any]
RouteEntry = Dict[str, Union[RouteHandler, List[str], Pattern[str]]]
RouteMatch = Tuple[RouteHandler, Dict[str, str]]


class Router:
    """
    A flexible URL router that handles path registration and matching with support for
    dynamic path parameters using regular expressions.

    Maps URL paths to handler functions with pattern matching capabilities for
    dynamic path segments, enabling parameterized routing and flexible URL
    structure handling in web applications.
    """

    routes: Dict[str, RouteEntry] = {}

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable[[T], T]:
        """
        Decorator to register a route handler with an optional list of HTTP methods.

        Converts dynamic path segments into regex capture groups and associates
        the path pattern with a handler function for request routing and parameter
        extraction during URL matching operations.

        Args:
            path: The route path pattern, which may include dynamic segments.
            methods: The list of allowed HTTP methods for this route.
                   Defaults to ["GET"] if not specified.

        Returns:
            A decorator function that registers the handler for the route.
        """
        if methods is None:
            methods = ["GET"]  # Default to GET if no methods are provided

        # Convert dynamic path segments like <id:int> to regex patterns with named capture groups
        # This allows for automatic parameter extraction when matching routes
        pattern = re.sub(r"<(\w+):(\w+)>", r"(?P<\1>[^/]+)", path)

        # Compile the pattern into a regex, ensuring it matches the entire path
        regex: Pattern[str] = re.compile(f"^{pattern}$")

        def decorator(handler: T) -> T:
            """
            Inner decorator function that registers the route in the router's routes dictionary.

            Args:
                handler: The function that handles requests to this route.

            Returns:
                The original handler function, unchanged.
            """
            # Store the route details: handler, allowed methods, and compiled regex pattern
            cls.routes[path] = {
                "handler": handler,
                "methods": methods,
                "pattern": regex,
            }
            return handler  # Return the original handler function unchanged

        return decorator

    @classmethod
    def match(cls, path: str, method: str) -> Optional[RouteMatch]:
        """
        Match an incoming request path and method against registered routes.

        Iterates through registered routes to find matching URL path patterns
        and HTTP methods, returning the associated handler function and extracted
        parameters for successful matches.

        Args:
            path: The request URL path to match.
            method: The HTTP method of the request (e.g., "GET", "POST").

        Returns:
            If a match is found, returns a tuple containing:
            - The route handler function
            - A dictionary of extracted parameters from the path
            If no match is found, returns None.
        """
        # Iterate over all registered routes to find a matching path and method
        for route in cls.routes.values():
            # Get the compiled regex pattern for this route
            pattern = cast(Pattern[str], route.get("pattern"))

            # Get allowed methods, defaulting to ["GET"] if none specified
            methods = cast(List[str], route.get("methods", ["GET"]))

            # Check if both the pattern matches the path AND the method is allowed
            match = pattern.match(path) if pattern else None
            if match and method in methods:
                # Extract the handler function
                handler = cast(RouteHandler, route["handler"])

                # Extract named parameters from the regex match
                params = match.groupdict()

                # Return the handler and extracted parameters
                return handler, params

        # No matching route found
        return None

    @classmethod
    def methods(cls, path: str) -> List[str]:
        """
        Get a list of HTTP methods allowed for a specific path.

        Determines allowed HTTP methods for a given path by matching against
        registered route patterns, useful for implementing OPTIONS requests
        and generating appropriate Allow headers for method validation.

        Args:
            path: The URL path to check for allowed methods.

        Returns:
            A list of allowed HTTP method strings for the path.
            Returns ["GET"] as default if the path is not registered.
        """
        # Iterate through registered routes to find a matching pattern
        for route in cls.routes.values():
            pattern = cast(Pattern[str], route.get("pattern"))

            # If this route's pattern matches the given path
            if pattern and pattern.match(path):
                # Return the allowed methods for this route
                return cast(List[str], route.get("methods", ["GET"]))

        # No matching route found, default to allowing only GET
        return ["GET"]