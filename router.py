from typing import Callable, Dict, List, Optional, Union


class Router:
    routes: Dict[str, Dict[str, Union[Callable, List[str]]]] = {}

    @classmethod
    def route(cls, path: str, methods: Optional[List[str]] = None) -> Callable[[Callable], Callable]:
        """Decorator to register routes"""
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            """Decorator function to register routes."""
            cls.routes[path] = {"handler": handler, "methods": methods}
            return handler
        return decorator

    @classmethod
    def get_route(cls, path: str) -> Optional[Dict[str, Union[Callable, List[str]]]]:
        """Get route handler for a given path."""
        return cls.routes.get(path)

    @classmethod
    def get_allowed_methods(cls, path: str) -> List[str]:
        """Get allowed HTTP methods for a given path."""
        route = cls.get_route(path)
        if route:
            return route.get("methods", ["GET"])
        return ["GET"]
