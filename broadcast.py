import json
from urllib.parse import parse_qs, urlparse

class Request:
    def __init__(self, handler):
        """
        Initialize a Request object.

        Args:
            handler: The HTTP request handler.
        """
        self.handler = handler
        self._parsed_url = urlparse(self.handler.path)
        self._query_params = parse_qs(self._parsed_url.query)

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
        return self._parsed_url.path
    
    @property
    def fragment(self):
        """
        Get the URL fragment.

        Returns:
            str: The URL fragment.
        """
        return self._parsed_url.fragment

    @property
    def headers(self):
        """
        Get the request headers.

        Returns:
            dict: A dictionary containing the request headers.
        """
        return self.handler.headers

    @property
    def queries(self):
        """
        Get the query parameters.

        Returns:
            dict: A dictionary of query parameters parsed from the URL.
        """
        return self._query_params

    def json(self):
        """
        Parse the request body as JSON.

        Returns:
            dict: The JSON data parsed from the request body.
        """
        content_length = int(self.handler.headers.get("Content-Length", 0))
        if content_length:
            post_data = self.handler.rfile.read(content_length)
            return json.loads(post_data.decode("utf-8"))
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
        self.body = b""

    def send(self):
        """
        Send the response.
        """
        self.handler.send_response(self.status_code)
        for key, value in self.headers.items():
            self.handler.send_header(key, value)
        self.handler.send_header("Content-Length", str(len(self.body)))
        self.handler.end_headers()
        self.handler.wfile.write(self.body)

    def json(self, data):
        """
        Set the response body to JSON data.

        Args:
            data: The JSON data to be included in the response body.
        """
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(data).encode("utf-8")
        self.send()

    def api(self, data=None):
        """
        Send an API response with appropriate status and data based on the HTTP method.

        Args:
            data (dict, optional): The data to be included in the response.
        """
        method = self.handler.command
        context = {
            "GET": lambda: (data if data is not None else {}, 200),
            "POST": lambda: ({"message": "Resource created", "data": data} if data is not None else {"message": "Resource created"}, 201),
            "PUT": lambda: ({"message": "Resource updated", "data": data} if data is not None else {"message": "Resource updated"}, 200),
            "DELETE": lambda: ({"message": "Resource deleted"}, 204),
        }

        response_data, status_code = context.get(method, lambda: ({"error": "Method not allowed"}, 405))()
        self.status_code = status_code
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(response_data).encode("utf-8")
        self.send()
