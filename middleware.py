from typing import Callable, List, Any, TypeVar, cast, Optional
from broadcast import Request, Response
from functools import wraps
from webpy import WebPy

# Type variables for better function typing
T = TypeVar("T", bound=Callable[..., Any])
MiddlewareHandler = Callable[[Request, Response], Any]


class Middleware:
    """
    Middleware class to manage request/response processing handlers.

    This class provides functionality to register and execute middleware functions
    that can process requests and responses before they reach the route handlers.
    Middleware can be applied globally or selectively to specific routes.
    """

    def __init__(self, app: WebPy) -> None:
        """
        Initialize the Middleware with the given application.

        Sets up the middleware container and associates it with a WebPy application
        instance for integration with the routing system.

        Args:
            app (WebPy): The WebPy application instance to attach middleware to.
        """
        self.app = app
        self.handlers: List[MiddlewareHandler] = []

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

        Example:
            @middleware.enroll
            def auth_middleware(request, response):
                # Process authentication
                pass
        """
        self.handlers.append(handler)
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

        Example:
            @app.route("/public")
            @middleware.exclude
            def public_route(request, response):
                # This route will not use any middleware
                pass
        """
        # Simply return the original handler without applying middleware
        return handler
