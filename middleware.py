from typing import Callable, List, Any, TypeVar, Dict
from broadcast import Request, Response
from webpy import WebPy

# Type variables for better function typing
T = TypeVar("T", bound=Callable[..., Any])
MiddlewareHandler = Callable[[Request, Response], Any]


class Middleware:
    """
    Middleware class to manage request/response processing handlers.

    This class provides functionality to register, execute, and manage middleware functions
    that can process requests and responses before they reach the route handlers.
    Middleware can be applied globally or selectively to specific routes, with options
    to group, skip, pause, resume or reset the execution chain as needed.
    """

    def __init__(self, app: WebPy) -> None:
        """
        Initialize the Middleware with the given application.

        Sets up the middleware container and associates it with a WebPy application
        instance for integration with the routing system.

        Args:
            app (WebPy): The WebPy application instance to attach middleware to.
        """
        self.app = app  # Store reference to the main app
        self.handlers: List[MiddlewareHandler] = []  # List of middleware handlers
        self.groups: Dict[str, List[MiddlewareHandler]] = {}  # Named groups of middleware

    def enroll(self, handler: MiddlewareHandler) -> MiddlewareHandler:
        """
        Enroll a middleware handler to be executed on requests.

        This method adds the middleware handler to the execution pipeline
        that processes each request before it reaches the route handler.

        Args:
            handler (MiddlewareHandler): The middleware function that accepts
                                        request and response objects.

        Returns:
            MiddlewareHandler: The registered middleware handler, unchanged.
        """
        self.handlers.append(handler)  # Add handler to the middleware pipeline
        return handler

    def exclude(self, handler: T) -> T:
        """
        Decorator to exclude middleware from being executed for the decorated route.

        This can be used to skip middleware processing for specific routes
        that don't require it.

        Args:
            handler (T): The route handler function.

        Returns:
            T: The original handler function, unchanged.
        """
        # Simply return the original handler without applying middleware
        return handler

    def reset(self) -> None:
        """
        Reset the middleware stack, clearing all registered handlers.

        This method removes all middleware handlers from the execution pipeline,
        effectively resetting the middleware configuration to its initial state.
        Useful for testing or when reconfiguring the application pipeline.
        """
        self.handlers.clear()  # Clear all registered handlers
        self.groups.clear()  # Clear middleware groups

    def group(self, name: str, *handlers: MiddlewareHandler) -> None:
        """
        Create a named group of middleware handlers for selective application.

        Groups allow organizing middleware functions into logical units that
        can be applied or removed together, providing better organization and
        control over the middleware execution flow.

        Args:
            name (str): The name of the middleware group.
            *handlers: One or more middleware handler functions to add to the group.
        """
        self.groups[name] = list(handlers)  # Store handlers in a named group

    def apply(self, name: str) -> None:
        """
        Apply a named middleware group to the handler stack.

        This adds all middleware handlers from the specified group to the
        active middleware pipeline, enabling modular middleware management.

        Args:
            name (str): The name of the middleware group to apply.)
        """
        # Add all handlers from the named group to the active pipeline
        if name in self.groups:
            self.handlers.extend(self.groups[name])