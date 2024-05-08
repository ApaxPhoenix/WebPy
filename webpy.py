from core import WebPyCore


class WebPy:
    def __init__(self):
        # Initialize WebPyCore as part of the WebPyApp
        self.app = WebPyCore

    def route(self, path, methods=None):
        """Decorator to register routes"""
        if methods is None:
            methods = ['GET']

        def decorator(handler):
            """
            Decorator function to register routes.

            Args:
                path (str): URL path to register the route.
                methods (list, optional): List of HTTP methods allowed for the route.

            Returns:
                function: Decorated handler function.
                :param handler: 
            """
            # Register the route with WebPyCore
            self.app.route(path, methods)(handler)
            return handler
        return decorator

    def run(self, ip=None, port=None):
        """
        Start the web application.

        Args:
            ip (str, optional): IP address to bind the server to. Defaults to '127.0.0.1'.
            port (int, optional): Port to listen on. Defaults to 8080.
        """
        # Run the web application with specified IP and port
        self.app.run(ip=ip, port=port)
