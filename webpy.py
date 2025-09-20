from typing import Callable, List, Optional, Any, Type, TypeVar, cast
from .core import WebPyCore
from .broadcast import Request, Response
from .middleware import Middleware
from .blueprint import Blueprint

# Enhanced type definitions for improved type safety and clarity
Handler = TypeVar("Handler", bound=Callable[..., Any])
ErrorHandler = TypeVar("ErrorHandler", bound=Callable[..., Any])
Processor = TypeVar("Processor", bound=Callable[[Request, Response], Any])


class WebPy:
    """
    Primary application class that orchestrates web framework functionality.

    This class serves as the main entry point for building web applications,
    providing comprehensive routing capabilities, middleware management, error
    handling, template rendering, blueprint integration, and server execution
    through a simplified and intuitive API interface designed for rapid
    development and scalable web application architecture.
    """

    def __init__(self) -> None:
        """
        Create a new web application instance.

        Establishes the underlying core server infrastructure, initializes
        the middleware processing pipeline, and prepares the application
        for route registration and request handling operations.
        """
        self.app: Type[WebPyCore] = WebPyCore
        self.middleware: Middleware = Middleware(self)

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None
    ) -> Callable[[Handler], Handler]:
        """
        Define URL routing for incoming HTTP requests with middleware integration.

        This decorator binds handler functions to specific URL patterns and
        HTTP methods, automatically integrating middleware processing into
        the request flow for comprehensive request handling and response processing.

        Parameters:
            path: URL pattern to match (supports dynamic path segments)
            methods: HTTP methods to accept (defaults to GET only)

        Returns:
            Decorator function for registering route handlers

        Raises:
            TypeError: When handler function signature is incompatible
        """
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Handler) -> Handler:
            """
            Bind the handler function to the specified route.

            Wraps the handler with middleware execution logic and
            registers it with the core routing engine for request processing.

            Parameters:
                handler: Function to process requests matching this route

            Returns:
                Original handler function (unmodified for external use)
            """

            # Middleware-aware wrapper for request processing
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                request = kwargs.get("request") or args[0]
                response = kwargs.get("response") or args[1]

                # Run pre-processing middleware pipeline
                if self.middleware.process(request, response):
                    # Execute the actual handler if middleware chain succeeds
                    result = handler(*args, **kwargs)

                    # Run post-processing middleware pipeline
                    for name, processor in self.middleware.map["after"].items():
                        processor(request, response)

                    return result
                return None

            # Register wrapped handler with the routing system
            self.app.route(path, methods)(wrapper)
            return cast(Handler, handler)

        return decorator

    def error(self, code: int) -> Callable[[ErrorHandler], ErrorHandler]:
        """
        Define custom handlers for HTTP error responses.

        This decorator allows registration of functions to handle specific
        HTTP status codes with custom error pages, logging, or alternative
        response strategies for improved user experience and debugging.

        Parameters:
            code: HTTP status code to intercept (404, 500, etc.)

        Returns:
            Decorator function for registering error handlers
        """

        def decorator(handler: ErrorHandler) -> ErrorHandler:
            """
            Register the handler for the specified error code.

            Connects the handler function to the HTTP status code in
            the application's error handling system for automatic invocation.

            Parameters:
                handler: Function to execute when this error occurs

            Returns:
                Original handler function (unmodified)
            """
            self.app.error(code)(handler)
            return cast(ErrorHandler, handler)

        return decorator

    def render(self, template: str, **context: Any) -> str:
        """
        Generate HTML from templates using the integrated template engine.

        Processes template files through Jinja2 with the provided data
        context to produce final HTML output ready for HTTP response delivery.

        Parameters:
            template: Template filename (relative to templates directory)
            **context: Data variables accessible within the template scope

        Returns:
            Rendered HTML content ready for HTTP response transmission
        """
        return self.app.render(template, **context)

    def blueprint(self, blueprint: Blueprint) -> None:
        """
        Integrate a blueprint module into the main application structure.

        Merges the blueprint's routes, templates, static resources, and
        middleware with the primary application for modular development
        and organized code architecture.

        Parameters:
            blueprint: Blueprint instance containing modular app components
        """
        blueprint.blueprint(self.app)

    def run(
        self,
        ip: str = "0.0.0.0",
        port: int = 8080,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
    ) -> None:
        """
        Launch the web server with configured application settings.

        Starts the HTTP or HTTPS server and begins processing incoming
        requests using all registered routes, middleware, and error handlers
        for complete web application functionality.

        Parameters:
            ip: Network interface address (default: all interfaces)
            port: TCP port for server binding (default: 8080)
            certfile: SSL certificate path (enables HTTPS when provided)
            keyfile: SSL private key path (required with certfile)

        Note:
            HTTPS mode requires both certfile and keyfile parameters.
            HTTP mode is used when SSL files are not provided.
        """
        self.app.run(ip=ip, port=port, certfile=certfile, keyfile=keyfile)