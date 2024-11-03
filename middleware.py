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
            app (WebPy): The application instance.
        """
        self.app = app
        self.objects: List[Callable[[Request, Response], Any]] = []

    def register(self, object: Callable[[Request, Response], Any]) -> Callable:
        """
        Register an object function to be executed on requests.

        Args:
            object (Callable[[Request, Response], Any]): The object function.

        Returns:
            Callable: The registered object function.
        """
        self.objects.append(object)
        return object

    def run(self, objects: List[Callable] = None) -> Callable:
        """
        Decorator to execute specified objects before the route function.
        If no objects are specified, runs all registered objects.

        Args:
            objects (List[Callable], optional): List of specific objects to run.

        Returns:
            Callable: The decorated function.
        """
        def decorator(handler: Callable) -> Callable:
            @wraps(handler)
            def wrapper(request: Request, response: Response, *args, **kwargs):
                # Run either specified objects or all registered objects
                pipeline = objects if objects is not None else self.objects
                for object in pipeline:
                    object(request, response)
                return handler(request, response, *args, **kwargs)
            return wrapper
        return decorator
