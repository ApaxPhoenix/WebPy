import json
from typing import Any, Dict, Optional, Union, List, cast
from urllib.parse import parse_qs, urlparse, ParseResult
from http.server import BaseHTTPRequestHandler
import warnings

# Type aliases for better code clarity
QueryDict = Dict[str, List[str]]  # The actual return type of parse_qs
HeadersDict = Dict[str, str]
JsonData = Dict[str, Any]
FormData = Dict[str, Any]  # Type alias for form data


class Request:
    """
    A Request object to encapsulate details of an HTTP request.

    This class provides an abstraction layer over the raw HTTP request,
    offering convenient access to common request properties such as
    method, path, headers, query parameters, cookies, and more.

    Attributes:
        handler (BaseHTTPRequestHandler): The underlying HTTP request handler.
        parsing (ParseResult): Parsed URL components of the request path.
        querier (QueryDict): Parsed query parameters from the URL.
    """

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Initialize a Request object with the provided HTTP handler.

        Args:
            handler (BaseHTTPRequestHandler): The HTTP request handler containing
                                             raw request information.
        """
        self.handler = handler
        # Parse the request path and query string into component parts
        self.parsing: ParseResult = urlparse(self.handler.path)
        # Parse query parameters and store them as a dictionary
        self.querier: QueryDict = parse_qs(self.parsing.query)

    @property
    def method(self) -> str:
        """
        Get the HTTP request method.

        Returns:
            str: The HTTP request method (e.g., "GET", "POST", "PUT", "DELETE").
        """
        return cast(str, self.handler.command)

    @property
    def path(self) -> str:
        """
        Get the request path component of the URL.

        This excludes query parameters and fragments.

        Returns:
            str: The request path (e.g., "/users/profile").
        """
        return self.parsing.path

    @property
    def fragment(self) -> str:
        """
        Get the URL fragment (the part after '#').

        Returns:
            str: The URL fragment or empty string if none exists.
        """
        return self.parsing.fragment

    @property
    def headers(self) -> HeadersDict:
        """
        Get all request headers as a dictionary.

        Returns:
            Dict[str, str]: A dictionary mapping header names to their values.
        """
        return dict(self.handler.headers)

    @property
    def queries(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the query parameters from the URL.

        Note that each parameter can have multiple values if specified multiple times in the URL.

        Returns:
            Dict[str, Union[str, List[str]]]: A dictionary of query parameters parsed from the URL.
                                             Values may be strings or lists of strings.
        """
        return self.querier

    @property
    def ip(self) -> str:
        """
        Get the client's IP address.

        Returns:
            str: The client's IP address.
        """
        return self.handler.client_address[0]

    def json(self) -> Optional[JsonData]:
        """
        Parse the request body as JSON.

        This method reads the request body data and attempts to parse it as JSON.
        It only reads data if Content-Length header is present and non-zero.

        Returns:
            Optional[Dict[str, Any]]: The JSON data parsed from the request body,
                                     or None if no data is present or parsing fails.
        """
        length = int(self.headers.get("Content-Length", "0"))
        if length > 0:
            try:
                data = self.handler.rfile.read(length)
                return json.loads(data.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None

class Response:
    """
    A Response object to encapsulate and build HTTP responses.

    This class provides methods for constructing HTTP responses with
    different status codes, headers, and body formats (especially JSON).

    Attributes:
        handler (BaseHTTPRequestHandler): The HTTP request handler used to send the response.
        status (int): The HTTP status code for the response (defaults to 200 OK).
        headers (Dict[str, str]): A dictionary of response headers.
        body (bytes): The response body as bytes.
    """

    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Initialize a Response object with the provided HTTP handler.

        Args:
            handler (BaseHTTPRequestHandler): The HTTP request handler that will
                                             be used to send the response.
        """
        self.handler = handler
        self.status: int = 200  # Default to 200 OK status
        self.headers: HeadersDict = {}  # Initialize headers as empty dictionary
        self.body: bytes = b""  # Initialize empty response body as bytes

    def send(self) -> None:
        """
        Send the complete HTTP response to the client.

        This method sends the status code, all headers, and the response body
        to the client in the proper HTTP format.
        """
        # Send the status code to the client
        self.handler.send_response(self.status)

        # Send all custom headers
        for key, value in self.headers.items():
            self.handler.send_header(str(key), str(value))

        # Always include Content-Length header based on body size
        self.handler.send_header("Content-Length", str(len(self.body)))

        # Signal end of headers section
        self.handler.end_headers()

        # Write the response body to the output stream
        self.handler.wfile.write(self.body)

    def json(self, data: JsonData) -> "Response":
        """
        Set the response body to JSON data and set appropriate headers.

        This method serializes the provided data to JSON, sets the Content-Type
        header appropriately, and returns self for method chaining.

        Args:
            data (Dict[str, Any]): The data to serialize as JSON in the response.

        Returns:
            Response: Self, for method chaining.
        """
        # Set JSON content type header
        self.headers["Content-Type"] = "application/json"

        # Convert data to JSON string and encode as UTF-8 bytes
        self.body = json.dumps(data).encode("utf-8")

        # Return self for method chaining (e.g., response.json(data).send())
        return self

    def api(self, data: Optional[JsonData] = None) -> "Response":
        """
        Create a standardized API response based on the HTTP method.

        This method generates consistent API responses with appropriate
        status codes and messages based on the request's HTTP method.

        The response structure varies by method:
        - GET: Returns the data directly or an empty object
        - POST: Returns "Resource created" message with 201 status and optional data
        - PUT: Returns "Resource updated" message with 200 status and optional data
        - DELETE: Returns "Resource deleted" message with 204 status
        - Others: Returns "Method not allowed" error with 405 status

        Args:
            data (Optional[Dict[str, Any]]): The data to include in the response (optional).

        Returns:
            Response: Self, for method chaining.
        """
        method = cast(str, self.handler.command)  # Get the HTTP method

        # Define response content and status code based on HTTP method
        context = {
            "GET": lambda: (data if data is not None else {}, 200),
            "POST": lambda: (
                (
                    {"message": "Resource created", "data": data}
                    if data
                    else {"message": "Resource created"}
                ),
                201,
            ),
            "PUT": lambda: (
                (
                    {"message": "Resource updated", "data": data}
                    if data
                    else {"message": "Resource updated"}
                ),
                200,
            ),
            "DELETE": lambda: ({"message": "Resource deleted"}, 204),
        }

        # Get the appropriate response handler based on method, or use default for unsupported methods
        handler = context.get(method, lambda: ({"error": "Method not allowed"}, 405))

        # Call the handler to get response data and status
        data, status = handler()

        # Set the determined status code
        self.status = status

        # Set content type to JSON
        self.headers["Content-Type"] = "application/json"

        # Encode response data to JSON format in bytes
        self.body = json.dumps(data).encode("utf-8")

        # Return self for method chaining
        return self

    def serve(self, filepath: str, mime: Optional[str] = None) -> "Response":
        """
        Serve a static file to the client.

        Args:
            filepath (str): The path to the file to serve.
            mime (Optional[str]): The MIME type of the file (optional).

        Returns:
            Response: Self, for method chaining.
        """
        try:
            with open(filepath, "rb") as file:
                self.body = file.read()

            # Set Content-Type header if MIME type is provided
            if mime:
                self.headers["Content-Type"] = mime
            else:
                # Guess MIME type based on file extension
                import mimetypes
                mime, _ = mimetypes.guess_type(filepath)
                if mime:
                    self.headers["Content-Type"] = mime

            # Set Content-Length header
            self.headers["Content-Length"] = str(len(self.body))

        except FileNotFoundError:
            warnings.warn("File not found")

        return self

    def redirect(self, url: str, status: int = 302) -> "Response":
        """
        Set up a redirect response to a different URL.

        This method configures the response with appropriate status code and
        Location header to redirect the client to the specified URL.

        Args:
            url (str): The URL to redirect to.
            status (int): The HTTP status code for the redirect (defaults to 302 Found).
                         Common redirect status codes:
                         - 301: Moved Permanently
                         - 302: Found (temporary redirect)
                         - 303: See Other
                         - 307: Temporary Redirect
                         - 308: Permanent Redirect

        Returns:
            Response: Self, for method chaining.
        """
        # Set the redirect status code
        self.status = status

        # Set the Location header with the target URL
        self.headers["Location"] = url

        # Set an empty body for the redirect response
        self.body = b""

        # Return self for method chaining
        return self