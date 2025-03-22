from typing import List, Callable, Dict, Optional, TypeVar, Any, cast
from pathlib import Path
from functools import wraps
from .router import Router
from jinja2 import ChoiceLoader, FileSystemLoader

# Enhanced type variables for better type safety
HandlerType = TypeVar("HandlerType", bound=Callable[..., Any])
RequestType = TypeVar("RequestType")
ResponseType = TypeVar("ResponseType")
ParamsType = TypeVar("ParamsType", bound=Dict[str, Any])
AppType = TypeVar("AppType")


class Blueprint:
    """
    Modular architecture component for web application organization.

    Encapsulates routes, templates, and static assets into independent modules
    that can be attached to the main application. Each Blueprint maintains its own
    isolated namespace with dedicated URL prefixing, template resolution, and
    static file serving capabilities.

    The Blueprint system enables:
    - Logical separation of application components
    - Reusable functional modules across projects
    - Domain-driven design at the routing level
    - Simplified maintenance through code isolation
    """

    # Global registry for all blueprint instances
    registry: Dict[str, 'Blueprint'] = {}

    def __init__(self, name: str, prefix: str = "") -> None:
        """
        Construct a new Blueprint instance with unique naming and routing.

        Parameters:
            name: Unique identifier for blueprint registration and template lookup
            prefix: URL prefix prepended to all routes within this blueprint

        Raises:
            KeyError: If blueprint with identical name already exists
        """
        self.name: str = name
        self.prefix: str = prefix.rstrip('/') if prefix else ''

        # Filesystem paths for blueprint resources
        self.directory: Path = Path("blueprints", name)
        self.template: Path = Path(self.directory, "templates")
        self.static: Path = Path(self.directory, "static")

        # Register in global blueprint registry for lookup
        Blueprint.registry[name] = self

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable[[HandlerType], HandlerType]:
        """
        Decorator factory for registering route handlers within this blueprint.

        Creates prefixed routes that maintain blueprint context during request
        processing, enabling proper template resolution and resource handling.

        Parameters:
            path: URL pattern to match (automatically prefixed with blueprint prefix)
            methods: HTTP methods supported by this route (defaults to GET only)

        Returns:
            Decorator function that processes and registers the handler

        Example:
            @users_blueprint.route('/profile/<id>')
            def profile(request, response, id):
                # Handles /users/profile/123 if prefix is 'users'
                return response.render('profile.html', user_id=id)
        """
        if methods is None:
            methods = ["GET"]

        # Decorator factory function
        def decoration(handler: HandlerType) -> HandlerType:
            # Construct full route path with blueprint prefix
            fullpath: str = f"{self.prefix}/{path.lstrip('/')}" if path else self.prefix

            # Register handler with router using wrapper for context
            @Router.route(fullpath, methods)
            @wraps(handler)
            def wrapper(request: RequestType, response: ResponseType, **params: Any) -> Any:
                # Preserve original render implementation
                original = response.__class__.render

                # Blueprint-aware template rendering function
                def render(template: str, **context: Any) -> str:
                    """
                    Enhanced template renderer with blueprint-first resolution.

                    Attempts to locate templates in the blueprint's directory before
                    falling back to global templates, enabling component isolation
                    while maintaining application-wide templates as fallbacks.

                    Parameters:
                        template: Template filename to render
                        **context: Variables to inject into template context

                    Returns:
                        Rendered template content as string
                    """
                    try:
                        # Check blueprint-specific template first
                        location: Path = Path(self.template, template)
                        if location.exists():
                            # Prefix template path with blueprint name
                            return original(f"{self.name}/{template}", **context)
                    except Exception:
                        # Silently handle resolution errors
                        pass

                    # Fall back to application-level template
                    return original(template, **context)

                # Monkey patch render method temporarily
                response.__class__.render = render

                try:
                    # Execute handler with enhanced context
                    result: Any = handler(request, response, **params)
                    return result
                finally:
                    # Restore original render method
                    response.__class__.render = original

            # Return wrapped handler with context
            return cast(HandlerType, wrapper)

        return decoration

    def register(self, app: AppType) -> None:
        """
        Integrate blueprint with main application infrastructure.

        Sets up template resolution paths and static file serving routes,
        making the blueprint's resources available to the application.

        Parameters:
            app: Main application instance to register with

        Side Effects:
            - Modifies app's template loader configuration
            - Adds static file routes to the application router
        """
        # Configure template resolution if templates exist
        if self.template.exists():
            # Collect existing template loaders
            loaders = []
            if hasattr(app.template, 'loader'):
                if hasattr(app.template.loader, 'loaders'):
                    loaders = list(app.template.loader.loaders)
                else:
                    loaders = [app.template.loader]

            # Create blueprint-specific template loader
            filesystem: FileSystemLoader = FileSystemLoader(str(self.template))

            # Chain loaders for hierarchical template resolution
            app.template.loader = ChoiceLoader(loaders + [filesystem])

        # Configure static file serving if static directory exists
        if self.static.exists():
            # Register route for blueprint's static assets
            @app.route(f"/static/{self.name}/<path:filepath>", methods=["GET"])
            def assets(request: RequestType, response: ResponseType, filepath: str) -> None:
                """
                Static file server for blueprint-specific assets.

                Serves files from the blueprint's static directory with
                appropriate MIME type detection and error handling.

                Parameters:
                    request: HTTP request object
                    response: HTTP response object for sending file
                    filepath: Relative path to requested file

                Responses:
                    200: File found and served with correct MIME type
                    404: File not found in blueprint's static directory
                    500: Error reading or processing file
                """
                resource: Path = Path(self.static, filepath)
                try:
                    # Read binary file content
                    with open(resource, "rb") as handle:
                        content: bytes = handle.read()

                    # MIME type detection based on file extension
                    extension: str = resource.suffix.lower()
                    mimetype: str = app.mimes.get(
                        extension, "application/octet-stream"
                    )

                    # Send response with proper content type
                    response.status(200).header("Content-Type", mimetype).send(content)
                except FileNotFoundError:
                    # File not found in static directory
                    response.status(404).text("File not found")
                except Exception as error:
                    # Handle IO errors, permission issues, etc.
                    response.status(500).text(f"Error: {str(error)}")