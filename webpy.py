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


web_app = WebPy()


@web_app.route("/hello", methods=['GET'])
def hello(request, response):
    if request.method == 'GET':
        id_param = request.params.get('id')
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hello Page</title>
        </head>
        <body>
            <h1>Hello, World!</h1>
            <p>ID: {id_param}</p>
        </body>
        </html>
        """
        response.headers['Content-Type'] = 'text/html'
        response.body = html_content.encode('utf-8')


web_app.run()
