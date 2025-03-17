from typing import Callable, List, Any, TypeVar, cast, Optional
from broadcast import Request, Response
from functools import wraps
from webpy import WebPy

# Type variables for better function typing
T = TypeVar('T', bound=Callable[..., Any])
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

    def register(self, handler: MiddlewareHandler) -> MiddlewareHandler:
        """
        Register a middleware handler to be executed on requests.

        This method adds the middleware handler to the execution pipeline
        that processes each request before it reaches the route handler.

        Args:
            handler (MiddlewareHandler): The middleware function that accepts
                                        request and response objects.

        Returns:
            MiddlewareHandler: The registered middleware handler, unchanged.

        Example:
            @middleware.register
            def auth_middleware(request, response):
                # Process authentication
                pass
        """
        self.handlers.append(handler)
        return handler

    def run(self, handlers: Optional[List[MiddlewareHandler]] = None) -> Callable[[T], T]:
        """
        Decorator to execute specified middleware handlers before the route function.

        If no handlers are specified, runs all registered middleware handlers in
        the order they were registered.

        Args:
            handlers (Optional[List[MiddlewareHandler]]): List of specific middleware
                                                         handlers to run. If None,
                                                         all registered handlers
                                                         will be executed.

        Returns:
            Callable[[T], T]: A decorator that applies middleware to the route handler.

        Example:
            @app.route("/protected")
            @middleware.run([auth_middleware, logging_middleware])
            def protected_route(request, response):
                # This route will use only auth and logging middleware
                pass

            @app.route("/public")
            @middleware.run()  # Use all registered middleware
            def public_route(request, response):
                # This route will use all middleware
                pass
        """

        def decorator(handler: T) -> T:
            """
            Inner decorator function that wraps the route handler with middleware.

            Args:
                handler (T): The route handler function.

            Returns:
                T: The wrapped handler function.
            """

            @wraps(handler)
            def wrapper(request: Request, response: Response, *args: Any, **kwargs: Any) -> Any:
                # Run either specified handlers or all registered handlers
                pipeline = handlers if handlers is not None else self.handlers
                for middleware_handler in pipeline:
                    middleware_handler(request, response)
                return handler(request, response, *args, **kwargs)

            return cast(T, wrapper)

        return decorator