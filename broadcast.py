import json
from typing import Any, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler


class Request:
    """
    A Request object to encapsulate details of an HTTP request.

    Attributes:
        handler (BaseHTTPRequestHandler): The HTTP request handler.
    """

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Initialize a Request object.

        Args:
            handler (BaseHTTPRequestHandler): The HTTP request handler.
        """
        self.handler = handler
        self.parsing = urlparse(self.handler.path)
        self.queries = parse_qs(self.parsing.query)

    @property
    def method(self) -> str:
        """
        Get the HTTP request method.

        Returns:
            str: The HTTP request method (e.g., "GET", "POST").
        """
        return self.handler.command

    @property
    def path(self) -> str:
        """
        Get the request path.

        Returns:
            str: The request path.
        """
        return self.parsing.path

    @property
    def fragment(self) -> str:
        """
        Get the URL fragment (the part after '#').

        Returns:
            str: The URL fragment.
        """
        return self.parsing.fragment

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the request headers.

        Returns:
            dict: A dictionary of request headers.
        """
        return dict(self.handler.headers)

    @property
    def queries(self) -> Dict[str, Union[str, list]]:
        """
        Get the query parameters from the URL.

        Returns:
            dict: A dictionary of query parameters parsed from the URL.
        """
        return self.queries

    def json(self):
        """
        Parse the request body as JSON.

        Returns:
            Optional[dict]: The JSON data parsed from the request body, or None if no data is present.
        """
        content = int(self.handler.headers.get("Content-Length", 0))
        print(content)
        if content and content is not None:
            post_data = self.handler.rfile.read(content)
            return json.loads(post_data.decode("utf-8"))
        return {}


class Response:
    """
    A Response object to encapsulate details of an HTTP response.

    Attributes:
        handler (BaseHTTPRequestHandler): The HTTP request handler.
        status (int): The HTTP status code for the response.
        headers (dict): A dictionary of response headers.
        body (bytes): The response body in bytes.
    """

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Initialize a Response object.

        Args:
            handler (BaseHTTPRequestHandler): The HTTP request handler.
        """
        self.handler = handler
        self.status = 200  # renamed from status_code to status
        self.headers: Dict[str, str] = {}
        self.body: bytes = bytes()

    def send(self) -> None:
        """
        Send the response back to the client.
        This includes the status code, headers, and body.
        """
        self.handler.send_response(self.status)
        # Ensure headers are correctly handled
        for key, value in self.headers.items():
            self.handler.send_header(str(key), str(value))
        self.handler.send_header("Content-Length", str(len(self.body)))
        self.handler.end_headers()
        self.handler.wfile.write(self.body)

    def json(self, data: Dict[str, Any]) -> None:
        """
        Set the response body to JSON data and send it.

        Args:
            data (dict): The JSON data to be included in the response body.
        """
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(data).encode("utf-8")
        self.send()

    def api(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Send an API response based on the HTTP method and data provided.

        This function builds standard responses for common HTTP methods like GET, POST, PUT, DELETE.

        Args:
            data (Optional[dict]): The data to be included in the response (optional).
        """
        method = self.handler.command
        context = {
            "GET": lambda: (data if data is not None else {}, 200),
            "POST": lambda: (
                {"message": "Resource created", "data": data} if data else {"message": "Resource created"}, 201),
            "PUT": lambda: (
                {"message": "Resource updated", "data": data} if data else {"message": "Resource updated"}, 200),
            "DELETE": lambda: ({"message": "Resource deleted"}, 204),
        }

        # Use the appropriate response for the HTTP method or return a 405 Method Not Allowed
        response, status = context.get(method, lambda: ({"error": "Method not allowed"}, 405))()
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(response).encode("utf-8")
        self.send()
