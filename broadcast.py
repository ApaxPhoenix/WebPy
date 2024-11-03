import json
from typing import Any, Dict, Optional, Union
from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler

class Request:
    """
    A Request object to encapsulate details of an HTTP request.

    Attributes:
        handler (BaseHTTPRequestHandler): The HTTP request handler.
        parsing (ParseResult): Parsed URL components of the request path.
        querier (Dict): Parsed query parameters from the URL.
    """

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Initialize a Request object.

        Args:
            handler (BaseHTTPRequestHandler): The HTTP request handler.
        """
        self.handler = handler
        # Parse the request path and query string, storing results in 'parsing'
        self.parsing = urlparse(self.handler.path)
        # Parse query parameters and store them as a dictionary in 'querier'
        self.querier = parse_qs(self.parsing.query)

    @property
    def method(self) -> str:
        """
        Get the HTTP request method.

        Returns:
            str: The HTTP request method (e.g., "GET", "POST").
        """
        return self.handler.command  # Retrieve the HTTP request method from the handler

    @property
    def path(self) -> str:
        """
        Get the request path.

        Returns:
            str: The request path.
        """
        return self.parsing.path  # Access the path component of the parsed URL

    @property
    def fragment(self) -> str:
        """
        Get the URL fragment (the part after '#').

        Returns:
            str: The URL fragment.
        """
        return self.parsing.fragment  # Access the fragment component of the parsed URL

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the request headers.

        Returns:
            dict: A dictionary of request headers.
        """
        return dict(self.handler.headers)  # Convert headers to a dictionary for easy access

    @property
    def queries(self) -> Dict[str, Union[str, list]]:
        """
        Get the query parameters from the URL.

        Returns:
            dict: A dictionary of query parameters parsed from the URL.
        """
        return self.querier  # Return the parsed query parameters

    def json(self) -> Optional[Dict[str, Any]]:
        """
        Parse the request body as JSON.

        Returns:
            Optional[dict]: The JSON data parsed from the request body, or None if no data is present.
        """
        # Convert headers to a dictionary and retrieve 'Content-Length', defaulting to 0
        content = int(dict(self.handler.headers).get("Content-Length", 0))

        # Read and parse JSON data only if content length is non-zero
        if content:
            data = self.handler.rfile.read(content)  # Read binary data from the request body
            return json.loads(data.decode("utf-8"))  # Decode binary data to a UTF-8 string and parse as JSON
        return None  # Return None if no JSON data is present

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
        self.status = 200  # Set the default status code to 200 (OK)
        self.headers: Dict[str, str] = {}  # Initialize headers as an empty dictionary
        self.body: bytes = bytes()  # Initialize an empty response body

    def send(self) -> None:
        """
        Send the response back to the client.
        This includes the status code, headers, and body.
        """
        self.handler.send_response(self.status)  # Send the status code to the client
        for key, value in self.headers.items():
            self.handler.send_header(str(key), str(value))  # Send each header key-value pair
        self.handler.send_header("Content-Length", str(len(self.body)))  # Add 'Content-Length' header
        self.handler.end_headers()  # Signal the end of the headers section
        self.handler.wfile.write(self.body)  # Write the response body to the output stream

    def json(self, data: Dict[str, Any]) -> None:
        """
        Set the response body to JSON data and send it.

        Args:
            data (dict): The JSON data to be included in the response body.
        """
        self.headers["Content-Type"] = "application/json"  # Set the header to indicate JSON content
        self.body = json.dumps(data).encode("utf-8")  # Encode JSON data to bytes
        self.send()  # Send the response with the JSON body

    def api(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Send an API response based on the HTTP method and data provided.

        This function builds standard responses for common HTTP methods like GET, POST, PUT, DELETE.

        Args:
            data (Optional[dict]): The data to be included in the response (optional).
        """
        method = self.handler.command  # Retrieve the HTTP method (e.g., "GET", "POST")

        # Define the response content and status code based on HTTP method
        context = {
            "GET": lambda: (data if data is not None else {}, 200),
            "POST": lambda: (
                {"message": "Resource created", "data": data} if data else {"message": "Resource created"}, 201),
            "PUT": lambda: (
                {"message": "Resource updated", "data": data} if data else {"message": "Resource updated"}, 200),
            "DELETE": lambda: ({"message": "Resource deleted"}, 204),
        }

        # Fetch response and status using the method's handler or default to 405 if method not allowed
        response, status = context.get(method, lambda: ({"error": "Method not allowed"}, 405))()
        self.status = status  # Set the determined status code
        self.headers["Content-Type"] = "application/json"  # Set content type to JSON
        self.body = json.dumps(response).encode("utf-8")  # Encode response data to JSON format in bytes
        self.send()  # Send the response back to the client