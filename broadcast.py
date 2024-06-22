import json
from urllib.parse import parse_qs


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
            str: The HTTP request method (e.g., "GET", "POST", "PUT", "DELETE").
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
