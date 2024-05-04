class Router:
    routes = {}

    @classmethod
    def route(cls, path, methods=None):
        """Decorator to register routes"""
        if methods is None:
            methods = ['GET']
            
        def decorator(handler):
            """Decorator function to register routes."""
            cls.routes[path] = {'handler': handler, 'methods': methods}
            return handler
        return decorator

    @classmethod
    def get_route(cls, path):
        """Get route handler for a given path."""
        return cls.routes.get(path)

    @classmethod
    def get_allowed_methods(cls, path):
        """Get allowed HTTP methods for a given path."""
        route = cls.get_route(path)
        if route:
            return route.get('methods', ['GET'])
        return ['GET']
    
