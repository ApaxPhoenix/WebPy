from typing import Callable, List, Any, TypeVar, Optional, cast
from broadcast import Request, Response

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

        Creates separate containers for preprocessing and postprocessing
        middleware functions and associates them with a WebPy application.

        Args:
            app: The WebPy application instance to attach middleware to.
        """
        self.app = app  # Reference to the main application
        self.guards: List[Processor] = []  # Preprocessing middleware (before)
        self.filters: List[Processor] = []  # Postprocessing middleware (after)

    def before(self, handler: Processor) -> Processor:
        """
        Register a middleware function to execute before route handlers.

        These functions can inspect and modify the incoming request,
        or halt the request processing pipeline if needed.

        Args:
            handler: Function that processes request and response objects
                    before the route handler executes.

        Returns:
            The registered middleware function, unchanged.
        """
        self.guards.append(handler)
        return cast(Processor, handler)

    def after(self, handler: Processor) -> Processor:
        """
        Register a middleware function to execute after route handlers.

        These functions can inspect and modify the outgoing response,
        such as adding headers or transforming the response body.

        Args:
            handler: Function that processes request and response objects
                    after the route handler executes but before the
                    response is sent to the client.

        Returns:
            The registered middleware function, unchanged.
        """
        self.filters.append(handler)
        return cast(Processor, handler)

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
        for guard in self.guards:
            # If any middleware returns False explicitly, halt execution
            result = guard(request, response)
            if result is False:
                return False

        # All preprocessing middleware executed successfully
        return True

    def filter(self, request: Request, response: Response) -> bool:
        """
        Execute all registered postprocessing middleware in sequence.

        Runs after the route handler and can modify the outgoing response
        before it's sent to the client.

        Args:
            request: The HTTP request object
            response: The HTTP response object

        Returns:
            Boolean indicating whether all middleware completed successfully.
            False means a middleware halted further processing.
        """
        for filter in self.filters:
            # If any middleware returns False explicitly, halt further processing
            result = filter(request, response)
            if result is False:
                return False

        # All postprocessing middleware executed successfully
        return True

    def use(self, handler: Processor) -> Processor:
        """
        Legacy method to register preprocessing middleware.

        Maintained for backward compatibility with existing code.
        Equivalent to calling before().

        Args:
            handler: Function that processes request and response objects

        Returns:
            The registered middleware function, unchanged.
        """
        return self.before(handler)