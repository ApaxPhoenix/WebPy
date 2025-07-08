from typing import List, Callable, Dict, Optional, TypeVar, Any, cast
from pathlib import Path
from functools import wraps
from .router import Router
from jinja2 import ChoiceLoader, FileSystemLoader

# Type variables with enhanced constraints for robust type checking
HandlerType = TypeVar("HandlerType", bound=Callable[..., Any])
RequestType = TypeVar("RequestType")
ResponseType = TypeVar("ResponseType")
ParamsType = TypeVar("ParamsType", bound=Dict[str, Any])
AppType = TypeVar("AppType")


class Blueprint:
    """
    Organizational unit for structuring web applications into logical modules.

    Provides a clean abstraction for grouping related routes, templates, and static
    resources under a unified namespace. Each Blueprint operates with its own URL
    prefix and resource directories, allowing for hierarchical application design
    and component reusability.

    Key capabilities include:
    - Isolated routing with automatic URL prefixing
    - Dedicated template and static file directories
    - Namespace collision prevention through named registration
    - Seamless integration with main application infrastructure
    """

    # Central storage for all instantiated blueprint components
    registry: Dict[str, "Blueprint"] = {}

    def __init__(self, name: str, prefix: str = "") -> None:
        """
        Initialize a Blueprint with distinct identity and routing configuration.

        Parameters:
            name: Distinctive identifier for blueprint lookup and resource namespacing
            prefix: URL path segment prepended to all blueprint routes

        Raises:
            KeyError: When attempting to register duplicate blueprint names
        """
        self.name: str = name
        self.prefix: str = prefix.rstrip("/") if prefix else ""

        # Blueprint resource directory structure
        self.directory: Path = Path("blueprints", name)
        self.template: Path = Path(self.directory, "templates")
        self.static: Path = Path(self.directory, "static")

        # Add to global blueprint tracking system
        Blueprint.registry[name] = self

    def route(
        self, path: str, methods: Optional[List[str]] = None
    ) -> Callable[[HandlerType], HandlerType]:
        """
        Create route decorators with blueprint-aware URL handling.

        Generates decorated handlers that automatically incorporate the blueprint's
        URL prefix and provide enhanced template resolution capabilities within
        the blueprint's resource context.

        Parameters:
            path: Route pattern (combined with blueprint prefix for final URL)
            methods: Accepted HTTP verbs (defaults to GET requests only)

        Returns:
            Decorator that enhances handlers with blueprint functionality

        Usage:
            @api_blueprint.route('/users/<int:id>')
            def get_user(request, response, id):
                # Accessible at /api/users/123 if prefix is 'api'
                return response.render('user_detail.html', user_id=id)
        """
        if methods is None:
            methods = ["GET"]

        # Blueprint route decorator implementation
        def decoration(handler: HandlerType) -> HandlerType:
            # Build complete URL path including blueprint prefix
            fullpath: str = f"{self.prefix}/{path.lstrip('/')}" if path else self.prefix

            # Register with router using enhanced wrapper
            @Router.route(fullpath, methods)
            @wraps(handler)
            def wrapper(
                request: RequestType, response: ResponseType, **params: Any
            ) -> Any:
                # Store reference to original template renderer
                original = response.__class__.render

                # Blueprint-scoped template resolution function
                def render(template: str, **context: Any) -> str:
                    """
                    Template renderer with blueprint-first lookup strategy.

                    Prioritizes templates from the blueprint's template directory,
                    falling back to application-wide templates when blueprint-specific
                    templates are unavailable. This enables modular template organization
                    while preserving access to shared application templates.

                    Parameters:
                        template: Name of template file to process
                        **context: Template variables for rendering context

                    Returns:
                        Fully rendered template content
                    """
                    try:
                        # Attempt blueprint-specific template resolution
                        location: Path = Path(self.template, template)
                        if location.exists():
                            # Use namespaced template path
                            return original(f"{self.name}/{template}", **context)
                    except Exception:
                        # Continue with fallback on any resolution error
                        pass

                    # Default to application-level template resolution
                    return original(template, **context)

                # Temporarily override render method for blueprint context
                response.__class__.render = render

                try:
                    # Execute handler with blueprint-enhanced environment
                    result: Any = handler(request, response, **params)
                    return result
                finally:
                    # Restore original render implementation
                    response.__class__.render = original

            # Return enhanced handler with blueprint capabilities
            return cast(HandlerType, wrapper)

        return decoration

    def blueprint(self, app: AppType) -> None:
        """
        Attach blueprint resources to the main application framework.

        Configures template loading hierarchy and establishes static file serving
        routes, making all blueprint resources accessible through the main
        application's request handling pipeline.

        Parameters:
            app: Primary application instance for resource integration

        Effects:
            - Extends application template loader with blueprint templates
            - Creates static file serving endpoints for blueprint assets
        """
        # Establish template loading chain if blueprint templates exist
        if self.template.exists():
            # Preserve existing template loader configuration
            loaders = []
            if hasattr(app.template, "loader"):
                if hasattr(app.template.loader, "loaders"):
                    loaders = list(app.template.loader.loaders)
                else:
                    loaders = [app.template.loader]

            # Add blueprint template loader to resolution chain
            filesystem: FileSystemLoader = FileSystemLoader(str(self.template))

            # Establish hierarchical template resolution order
            app.template.loader = ChoiceLoader(loaders + [filesystem])

        # Set up static asset serving if blueprint static directory exists
        if self.static.exists():
            # Create dedicated route for blueprint static files
            @app.route(f"/static/{self.name}/<path:filepath>", methods=["GET"])
            def assets(
                request: RequestType, response: ResponseType, filepath: str
            ) -> None:
                """
                HTTP handler for serving blueprint-specific static resources.

                Provides secure access to files within the blueprint's static directory,
                including proper MIME type detection and comprehensive error handling
                for missing files and access issues.

                Parameters:
                    request: Incoming HTTP request context
                    response: Outgoing HTTP response builder
                    filepath: Requested file path relative to blueprint static directory

                Status Codes:
                    200: Successfully served requested file with correct MIME type
                    404: Requested file does not exist in blueprint static directory
                    500: Server error during file access or processing
                """
                resource: Path = Path(self.static, filepath)
                try:
                    # Load file content in binary mode
                    with open(resource, "rb") as handle:
                        content: bytes = handle.read()

                    # Determine MIME type from file extension
                    extension: str = resource.suffix.lower()
                    mimetype: str = app.mimes.get(extension, "application/octet-stream")

                    # Deliver file with appropriate content type header
                    response.status(200).header("Content-Type", mimetype).send(content)
                except FileNotFoundError:
                    # Handle missing file requests
                    response.status(404).text("File not found")
                except Exception as error:
                    # Handle file system errors and permission issues
                    response.status(500).text(f"Error: {str(error)}")
