from typing import Callable, List, Optional, Any, Type, TypeVar, cast
from .core import WebPyCore
from .broadcast import Request, Response
from .middleware import Middleware
from .blueprint import Blueprint

# Type variables for function typing with proper constraints
Handler = TypeVar("Handler", bound=Callable[..., Any])
ErrorHandler = TypeVar("ErrorHandler", bound=Callable[..., Any])
Processor = TypeVar("Processor", bound=Callable[[Request, Response], Any])


class WebPy:
    """
    Main framework class for creating web applications.

    Provides a clean API for routing, middleware, error handling,
    template rendering, and server configuration. Acts as a high-level
    facade over the lower-level WebPyCore implementation.
    """

    def __init__(self) -> None:
        """
        Initialize a new web application instance.

        Sets up the core HTTP server reference and initializes the
        middleware management system.
        """
        self.app: Type[WebPyCore] = WebPyCore
        self.middleware = Middleware(self)

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[Handler], Handler]:
        """
        Register route handlers for URL paths and HTTP methods.

        Creates a decorator that maps a function to a specific URL path
        and HTTP method combination, wrapping it with middleware execution.

        Args:
            path: URL pattern for the route (can include dynamic segments)
            methods: List of HTTP methods this route responds to.
                     Defaults to ["GET"] if not specified.

        Returns:
            A decorator function that registers the handler with the routing system
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Handler) -> Handler:
            """
            Register the decorated function as a route handler.

            Wraps the original handler with middleware execution
            logic before registering it with the core routing system.

            Args:
                handler: The function that processes requests to this route

            Returns:
                The original handler function, unchanged
            """

            # Create a wrapper that applies middleware around the handler
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                request = kwargs.get('request') or args[0]
                response = kwargs.get('response') or args[1]

                # Execute preprocessing middleware chain
                if self.middleware.process(request, response):
                    # Only call the handler if preprocessing completed successfully
                    result = handler(*args, **kwargs)

                    # Execute postprocessing middleware chain
                    for name, processor in self.middleware.map["after"].items():
                        processor(request, response)

                    return result
                return None

            # Register the wrapped handler with the routing system
            self.app.route(path, methods)(wrapper)
            return cast(Handler, handler)

        return decorator

    def error(self, code: int) -> Callable[[ErrorHandler], ErrorHandler]:
        """
        Register custom error handlers for HTTP status codes.

        Creates a decorator that maps a function to a specific HTTP
        error code, allowing for custom error pages or responses.

        Args:
            code: HTTP status code to handle (e.g., 404, 500)

        Returns:
            A decorator that registers the error handler function
        """

        def decorator(handler: ErrorHandler) -> ErrorHandler:
            """
            Register the decorated function as an error handler.

            Maps the function to the specified HTTP status code in
            the underlying routing system.

            Args:
                handler: The function that will handle the specific error

            Returns:
                The original handler function, unchanged
            """
            self.app.error(code)(handler)
            return cast(ErrorHandler, handler)

        return decorator

    def render(self, template: str, **context: Any) -> str:
        """
        Render an HTML template with the provided context.

        Uses the Jinja2 templating engine integrated with WebPyCore
        to generate HTML from templates and data.

        Args:
            template: Name of the template file in the templates directory
            **context: Variables to make available in the template context

        Returns:
            The rendered HTML content as a string
        """
        return self.app.render(template, **context)

    def register(self, blueprint: Blueprint) -> None:
        """
        Register a blueprint with the application.

        Integrates the blueprint's routes, templates, and static assets
        into the main application.

        Args:
            blueprint: The blueprint instance to register
        """
        blueprint.register(self.app)

    def run(
            self,
            ip: str = "0.0.0.0",
            port: int = 8080,
            certfile: Optional[str] = None,
            keyfile: Optional[str] = None,
    ) -> None:
        """
        Start the web application server.

        Initializes and runs the HTTP/HTTPS server with all configured
        routes, middleware, and error handlers.

        Args:
            ip: IP address to bind the server to. Default is all interfaces.
            port: Port number to listen on. Default is 8080.
            certfile: Path to SSL certificate file for HTTPS.
                      Required with keyfile for HTTPS support.
            keyfile: Path to SSL key file for HTTPS.
                     Required with certfile for HTTPS support.

        Note:
            Providing both certfile and keyfile enables HTTPS.
            Otherwise, standard HTTP will be used.
        """
        self.app.run(ip=ip, port=port, certfile=certfile, keyfile=keyfile)