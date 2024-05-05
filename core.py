from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from router import Router
from broadcast import Request, Response


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
