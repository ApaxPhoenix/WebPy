from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import json

class Request:
    def __init__(self, handler):
        self.handler = handler

    @property
    def method(self):
        return self.handler.command

    @property
    def path(self):
        return self.handler.path

    @property
    def query_params(self):
        parsed_url = urlparse(self.path)
        return parse_qs(parsed_url.query)

    @property
    def fragment(self):
        parsed_url = urlparse(self.path)
        return parsed_url.fragment

    def json(self):
        content_length = int(self.handler.headers.get('Content-Length', 0))
        post_data = self.handler.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))


class Response:
    def __init__(self, handler):
        self.handler = handler
        self.status_code = 200
        self.headers = {}
        self.body = b''

    def send(self):
        self.handler.send_response(self.status_code)
        for key, value in self.headers.items():
            self.handler.send_header(key, value)
        self.handler.end_headers()
        self.handler.wfile.write(self.body)

    def json(self, data):
        self.headers['Content-Type'] = 'application/json'
        self.body = json.dumps(data).encode('utf-8')
        self.send()


class WebPyCore(BaseHTTPRequestHandler):
    router = {}
    template_env = Environment(loader=FileSystemLoader(Path("templates")))
    static_env = Path("static")
    
    @classmethod
    def route(cls, path, methods=['GET']):
        """Decorator to register routes"""
        def decorator(handler):
            cls.router[path] = {'handler': handler, 'methods': methods}
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
            request = Request(self)
            self.handle_route_request(method, request)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_route_request(self, method, request):
        try:
            handler_info = self.router.get(request.path)
            if handler_info:
                allowed_methods = handler_info.get('methods', ['GET'])
                if method in allowed_methods:
                    handler = handler_info['handler']
                    response = Response(self)
                    handler(request, response)
                    response.send()
                else:
                    self.send_error(405, f"Method {method} not allowed")
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
    def run(cls, server_class=HTTPServer, handler_class=None, ip=None, port=None):
        if handler_class is None:
            handler_class = cls
        try:
            server_address = (ip, port)
            httpd = server_class(server_address, handler_class)
            print(f"Starting server on {ip}:{port}")
            httpd.serve_forever()
        except OSError:
            print(f"Port {port} is in use")