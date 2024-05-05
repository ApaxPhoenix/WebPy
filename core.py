import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class Request:
    def __init__(self, handler):
        """
        Initialize a Request object.

        Args:
            handler: The HTTP request handler.
        """
        self.handler = handler

    @property
    def method(self):
        """
        Get the HTTP request method.

        Returns:
            str: The HTTP request method (e.g., "GET", "POST").
        """
        return self.handler.command

    @property
    def path(self):
        """
        Get the request path.

        Returns:
            str: The request path.
        """
        return self.handler.path

    @property
    def headers(self):
        """
        Get the request headers.

        Returns:
            dict: A dictionary containing the request headers.
        """
        return self.handler.headers

    @property
    def params(self):
        """
        Get the query parameters from the request URL.

        Returns:
            dict: A dictionary containing the query parameters.
        """
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)

    @property
    def fragment(self):
        """
        Get the fragment from the request URL.

        Returns:
            str: The fragment from the request URL.
        """
        parsed_url = urlparse(self.path)
        return parsed_url.fragment

    def json(self):
        """
        Parse the request body as JSON.

        Returns:
            dict: The JSON data parsed from the request body.
        """
        content_length = int(self.handler.headers.get('Content-Length', 0))
        if content_length:
            post_data = self.handler.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        else:
            return {}

class Response:
    def __init__(self, handler):
        """
        Initialize a Response object.

        Args:
            handler: The HTTP request handler.
        """
        self.handler = handler
        self.status_code = 200
        self.headers = {}
        self.body = b''

    def send(self):
        """Send the response."""
        self.handler.send_response(self.status_code)
        for key, value in self.headers.items():
            self.handler.send_header(key, value)
        self.handler.end_headers()
        self.handler.wfile.write(self.body)

    def json(self, data):
        """
        Set the response body to JSON data.

        Args:
            data: The JSON data to be included in the response body.
        """
        self.headers['Content-Type'] = 'application/json'
        self.body = json.dumps(data).encode('utf-8')
        self.send()

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

class WebPyCore(BaseHTTPRequestHandler):
    template_env = Environment(loader=FileSystemLoader(Path("templates")))
    static_env = Path("static")

    @classmethod
    def route(cls, path, methods=None):
        """Decorator to register routes"""
        if methods is None:
            methods = ['GET']

        def decorator(handler):
            """Decorator function to register routes."""
            Router.route(path, methods)(handler)
            return handler

        return decorator

    def do_GET(self):
        """Handle HTTP GET requests."""
        self.handle_request("GET")

    def do_POST(self):
        """Handle HTTP POST requests."""
        self.handle_request("POST")

    def do_DELETE(self):
        """Handle HTTP DELETE requests."""
        self.handle_request("DELETE")

    def handle_request(self, method):
        """Handle HTTP requests."""
        try:
            request = Request(self)
            self.handle_route_request(method, request)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_route_request(self, method, request):
        """Handle requests for registered routes."""
        try:
            # Remove query parameters from the path for route matching
            path_without_query = request.path.split('?', 1)[0]
            handler_info = Router.get_route(path_without_query)
            if handler_info:
                allowed_methods = Router.get_allowed_methods(path_without_query)
                if method in allowed_methods:
                    handler = handler_info['handler']
                    response = Response(self)
                    handler(request, response)
                    response.send()
                else:
                    self.send_error(405, f"Method {method} not allowed")
            elif request.path.startswith('/static/'):
                self.serve_static_file(request.path)
            else:
                self.send_error(404, "Not Found")
        except Exception as error:
            self.send_error(500, f"Internal Server Error: {str(error)}")
    
            
    def serve_static_file(self, path):
        """Serve static files."""
        relative_path = path[len('/static/'):]
        try:
            file_path = Path(self.static_env, relative_path)
            with open(file_path, "rb") as file:
                self.send_response(200)
                if path.endswith(".css"):
                    self.send_header('Content-type', 'text/css')
                elif path.endswith(".js"):
                    self.send_header('Content-type', 'application/javascript')
                else:
                    self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404)

    def render_template(self, template_name, **kwargs):
        """Render Jinja2 template."""
        template = self.template_env.get_template(template_name)
        return template.render(**kwargs)

    @classmethod
    def run(cls, ip=None, port=None, server_class=HTTPServer, handler_class=None):
        """Start the web server."""
        if handler_class is None:
            handler_class = cls
        try:
            server_address = (ip or '127.0.0.1', port or 8080)
            httpd = server_class(server_address, handler_class)
            print(f"Starting server on {server_address[0]}:{server_address[1]}")
            httpd.serve_forever()
        except OSError as e:
            print(f"Error starting server: {e}")

web_app = WebPyCore

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
