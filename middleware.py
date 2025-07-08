from __future__ import annotations
from typing import Callable, Dict, Any, TypeVar, Optional, cast, overload
from .broadcast import Request, Response

# Type variables for better function typing
Handler = TypeVar("Handler", bound=Callable[..., Any])
Processor = Callable[[Request, Response], Optional[bool]]


class Middleware:
    """
    Middleware management system for WebPy applications.

    Provides a way to register functions that run before and after
    route handlers, allowing for request/response modification,
    logging, authentication, and other cross-cutting concerns.
    """

    def __init__(self, app: Any) -> None:
        """
        Initialize the middleware system.

        Creates a container for middleware functions and
        associates them with a WebPy application.

        Args:
            app: The WebPy application instance to attach middleware to.
        """
        self.app = app  # Reference to the main application
        self.map: Dict[str, Dict[str, Processor]] = {
            "before": {},  # Preprocessing middleware
            "after": {},  # Postprocessing middleware
        }

    @overload
    def before(self, name: str, handler: Processor) -> Processor: ...

    @overload
    def before(self, name: str) -> Callable[[Processor], Processor]: ...

    def before(
        self, name: str, handler: Optional[Processor] = None
    ) -> Processor | Callable[[Processor], Processor]:
        """
        Register a middleware function to execute before route handlers.

        These functions can inspect and modify the incoming request,
        or halt the request processing pipeline if needed.

        Args:
            name: Unique identifier for this middleware function
            handler: Function that processes request and response objects
                    before the route handler executes.

        Returns:
            The registered middleware function, unchanged.
        """
        if handler is not None:
            # Direct registration
            self.map["before"][name] = handler
            return cast(Processor, handler)
        else:
            # Decorator registration
            def decorator(handler: Processor) -> Processor:
                self.map["before"][name] = handler
                return handler

            return decorator

    @overload
    def after(self, name: str, handler: Processor) -> Processor: ...

    @overload
    def after(self, name: str) -> Callable[[Processor], Processor]: ...

    def after(
        self, name: str, handler: Optional[Processor] = None
    ) -> Processor | Callable[[Processor], Processor]:
        """
        Register a middleware function to execute after route handlers.

        These functions can inspect and modify the outgoing response,
        such as adding headers or transforming the response body.

        Args:
            name: Unique identifier for this middleware function
            handler: Function that processes request and response objects
                    after the route handler executes but before the
                    response is sent to the client.

        Returns:
            The registered middleware function, unchanged.
        """
        if handler is not None:
            # Direct registration
            self.map["after"][name] = handler
            return cast(Processor, handler)
        else:
            # Decorator registration
            def decorator(handler: Processor) -> Processor:
                self.map["after"][name] = handler
                return handler

            return decorator

    def process(self, request: Request, response: Response) -> bool:
        """
        Execute all registered preprocessing middleware in sequence.

        Runs before the route handler and can modify the incoming request
        or prevent further processing.

        Args:
            request: The HTTP request object
            response: The HTTP response object

        Returns:
            Boolean indicating whether all middleware completed successfully.
            True means continue to the route handler, False means stop processing.
        """
        for name, handler in self.map["before"].items():
            # If any middleware returns False explicitly, halt execution
            result = handler(request, response)
            if result is False:
                return False

        # All preprocessing middleware executed successfully
        return True
