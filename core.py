from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class WebPyCore(BaseHTTPRequestHandler):
    router = {}
    template_env = Environment(loader=FileSystemLoader(Path("templates")))
    static_env = Path("static")
    
    @classmethod
    def route(cls, path):
        """Decorator to register routes"""
        def decorator(handler):
            cls.router[path] = handler
            return handler
        return decorator

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def handle_request(self, method):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}  # Parse query parameters
            fragment = parsed_url.fragment
            self.handle_route_request(method, path, query_params, fragment)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_route_request(self, method, path, query_params, fragment):
        try:
            if method == "GET" and path.startswith('/static'):
                self.serve_static_file(path)
            else:
                handler = self.router.get(path)
                if handler:
                    handler(self, query_params, fragment)
                else:
                    self.send_error(404, "Not Found")
        except Exception as error:
            self.send_error(500, f"Internal Server Error: {str(error)}")

    def serve_static_file(self, path):
        """Serve static files"""
        if path.startswith('/static/'):
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
                    return
            except FileNotFoundError:
                self.send_error(404)

    def render_template(self, template_name, **kwargs):
        """Render Jinja2 template"""
        template = self.template_env.get_template(template_name)
        return template.render(**kwargs)
    
    @classmethod
    def run(cls, server_class=HTTPServer, handler_class=None, ip='127.0.0.1', port=8085):
        if handler_class is None:
            handler_class = cls
        try:
            server_address = (ip, port)
            httpd = server_class(server_address, handler_class)
            print(f"Starting server on {ip}:{port}")
            httpd.serve_forever()
        except OSError:
            print(f"Port {port} is in use")