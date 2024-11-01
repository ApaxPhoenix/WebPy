from typing import Callable, List, Any
from broadcast import Request, Response
from functools import wraps
from webpy import WebPy


class Middleware:
    """Middleware class to manage request/response processing handlers."""

    def __init__(self, app: WebPy) -> None:
        """
        Initialize the Middleware with the given application.

        Args:
            app (WebPyCore): The application instance.
        """
        self.app = app
        self.handlers: List[Callable[[Request, Response], Any]] = []

    def register(self, handler: Callable[[Request, Response], Any]) -> Callable:
        """
        Register a handler function to be executed on requests.

        Args:
            handler (Callable[[Request, Response], Any]): The handler function.

        Returns:
            Callable: The registered handler function.
        """
        self.handlers.append(handler)
        return handler

    def run(self, handlers: List[Callable] = None) -> Callable:
        """
        Decorator to execute specified handlers before the route function.
        If no handlers are specified, runs all registered handlers.

        Args:
            handlers (List[Callable], optional): List of specific handlers to run.

        Returns:
            Callable: The decorated function.
        """
        def decorator(routing: Callable) -> Callable:
            @wraps(routing)
            def wrapper(request: Request, response: Response, *args, **kwargs):
                # Run either specified handlers or all registered handlers
                pipeline = handlers if handlers is not None else self.handlers
                for handler in pipeline:
                    handler(request, response)
                return routing(request, response, *args, **kwargs)
            return wrapper
        return decorator