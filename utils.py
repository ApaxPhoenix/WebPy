from urllib.parse import urlparse, parse_qs
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

