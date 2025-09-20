import json
from typing import Any, Dict, Optional, Union, List, cast, TypeVar, Callable, Tuple
from urllib.parse import parse_qs, urlparse, ParseResult
from http.server import BaseHTTPRequestHandler
import warnings
import mimetypes
from pathlib import Path

# Type variables for fluent interface pattern
R = TypeVar("R", bound="Response")

# Type aliases for semantic clarity
QueryDict = Dict[str, List[str]]  # Result structure from parse_qs
HeadersDict = Dict[str, str]  # HTTP headers mapping
JsonData = Dict[str, Any]  # JSON-serializable dictionary
FormData = Dict[str, Any]  # Form submission data
HttpHandler = BaseHTTPRequestHandler  # HTTP server handler


class Request:
    """
    HTTP request encapsulation providing structured access to request data.

    Abstracts the underlying HTTP request details into a convenient interface,
    offering simple property access to common request components including
    method, path, query parameters, headers, and body content for simplified
    request processing and type-safe operation handling.
    """

    def __init__(self, handler: HttpHandler) -> None:
        """
        Initialize request object from raw HTTP handler.

        Parameters:
            handler: Raw HTTP request handler containing connection details
        """
        self.handler: HttpHandler = handler
        # Extract and parse URL components
        self.components: ParseResult = urlparse(self.handler.path)
        # Parse query string into structured dictionary
        self.parameters: QueryDict = parse_qs(self.components.query)

    @property
    def method(self) -> str:
        """
        Retrieve the HTTP method used for this request.

        Returns:
            Uppercase HTTP method string (GET, POST, PUT, DELETE, etc.)
        """
        return cast(str, self.handler.command)

    @property
    def path(self) -> str:
        """
        Extract the URL path component without query parameters.

        Returns:
            URL path starting with forward slash (e.g., "/users/profile")
        """
        return self.components.path

    @property
    def fragment(self) -> str:
        """
        Extract the URL fragment identifier (portion after #).

        Returns:
            Fragment string without the # character, or empty string if none
        """
        return self.components.fragment

    @property
    def headers(self) -> HeadersDict:
        """
        Access all HTTP request headers.

        Returns:
            Dictionary mapping header names to their values
        """
        return dict(self.handler.headers)

    @property
    def queries(self) -> Dict[str, Union[str, List[str]]]:
        """
        Access query parameters from URL.

        Provides structured access to URL query parameters, handling
        multiple values for the same parameter name appropriately.

        Returns:
            Dictionary where keys are parameter names and values are either
            single strings or lists of strings for multi-valued parameters
        """
        return {k: v[0] if len(v) == 1 else v for k, v in self.parameters.items()}

    @property
    def ip(self) -> str:
        """
        Get client's IP address.

        Returns:
            String representation of client's IP address
        """
        return self.handler.client_address[0]

    def json(self) -> Optional[JsonData]:
        """
        Parse request body as JSON data.

        Attempts to read and parse the request body as JSON if Content-Length
        header indicates data is available. Handles encoding and parsing errors
        gracefully by returning None.

        Returns:
            Parsed JSON data as dictionary, or None if parsing fails or no data present
        """
        length: int = int(self.headers.get("Content-Length", "0"))
        if length > 0:
            try:
                content: bytes = self.handler.rfile.read(length)
                return json.loads(content.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None


class Response:
    """
    HTTP response builder with fluent interface for chaining operations.

    Provides a clean API for constructing HTTP responses with various
    content types, status codes, and headers. Supports method chaining
    for concise response construction and standardized API responses
    across different HTTP methods and content formats.
    """

    def __init__(self, handler: HttpHandler) -> None:
        """
        Initialize response builder with HTTP handler.

        Parameters:
            handler: HTTP handler for sending the response
        """
        self.handler: HttpHandler = handler
        self.status: int = 200  # Default success status
        self.headers: HeadersDict = {}  # Empty headers collection
        self.body: bytes = b""  # Empty response body

    def send(self) -> None:
        """
        Transmit the complete response to the client.

        Finalizes the response by sending status code, headers, and body
        to the client in proper HTTP format. This method should be called
        after all response configuration is complete.
        """
        # Send status line
        self.handler.send_response(self.status)

        # Send all custom headers
        for name, value in self.headers.items():
            self.handler.send_header(str(name), str(value))

        # Ensure Content-Length is always present
        self.handler.send_header("Content-Length", str(len(self.body)))

        # Mark end of headers section
        self.handler.end_headers()

        # Transmit response body
        self.handler.wfile.write(self.body)

    def json(self, data: JsonData) -> R:
        """
        Configure response with JSON content.

        Serializes data to JSON format and sets appropriate Content-Type
        header for JSON responses.

        Parameters:
            data: Dictionary to serialize as JSON

        Returns:
            Self for method chaining
        """
        # Set JSON media type
        self.headers["Content-Type"] = "application/json"

        # Serialize and encode data
        self.body = json.dumps(data).encode("utf-8")

        # Enable method chaining
        return cast(R, self)

    def api(self, data: Optional[JsonData] = None) -> R:
        """
        Generate standardized API response based on HTTP method.

        Creates consistent API responses with appropriate status codes
        and messages tailored to the request's HTTP method with standard
        REST conventions for different operations and resource interactions.

        Parameters:
            data: Optional payload to include in response

        Returns:
            Self for method chaining
        """
        method: str = cast(str, self.handler.command)

        # Method-specific response handlers
        responses: Dict[str, Callable[[], Tuple[JsonData, int]]] = {
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

        # Select appropriate handler or default to method not allowed
        handler: Callable[[], Tuple[JsonData, int]] = responses.get(
            method, lambda: ({"error": "Method not allowed"}, 405)
        )

        # Generate response data and status
        payload, statuscode = handler()

        # Configure response
        self.status = statuscode
        self.headers["Content-Type"] = "application/json"
        self.body = json.dumps(payload).encode("utf-8")

        return cast(R, self)

    def serve(self, filepath: str, mimetype: Optional[str] = None) -> R:
        """
        Serve static file as response.

        Reads file content and determines appropriate MIME type
        for Content-Type header, either from provided argument
        or by guessing based on file extension.

        Parameters:
            filepath: Path to file that should be served
            mimetype: Optional explicit MIME type to use

        Returns:
            Self for method chaining
        """
        try:
            location: Path = Path(filepath)
            with open(location, "rb") as filehandle:
                self.body = filehandle.read()

            # Set content type either from argument or by guessing
            if mimetype:
                self.headers["Content-Type"] = mimetype
            else:
                # Auto-detect MIME type
                detected, _ = mimetypes.guess_type(location)
                if detected:
                    self.headers["Content-Type"] = detected

            # Set content length
            self.headers["Content-Length"] = str(len(self.body))

        except FileNotFoundError:
            warnings.warn("File not found")

        return cast(R, self)

    def redirect(self, destination: str, statuscode: int = 302) -> R:
        """
        Configure response as HTTP redirect.

        Sets up appropriate status code and Location header
        to redirect client to specified URL with standard
        HTTP redirect status codes and proper header configuration.

        Parameters:
            destination: Target URL for redirect
            statuscode: HTTP status code to use (default: 302 Found)

        Returns:
            Self for method chaining
        """
        # Set redirect status
        self.status = statuscode

        # Set target location
        self.headers["Location"] = destination

        # Empty body for redirect
        self.body = b""

        return cast(R, self)

    def text(self, content: str) -> R:
        """
        Configure response with plain text content.

        Sets Content-Type header for text and encodes content
        as UTF-8 bytes.

        Parameters:
            content: Text string to include in response

        Returns:
            Self for method chaining
        """
        # Set plain text media type
        self.headers["Content-Type"] = "text/plain; charset=utf-8"

        # Encode content
        self.body = content.encode("utf-8")

        return cast(R, self)

    def html(self, content: str) -> R:
        """
        Configure response with HTML content.

        Sets Content-Type header for HTML and encodes content
        as UTF-8 bytes.

        Parameters:
            content: HTML string to include in response

        Returns:
            Self for method chaining
        """
        # Set HTML media type
        self.headers["Content-Type"] = "text/html; charset=utf-8"

        # Encode content
        self.body = content.encode("utf-8")

        return cast(R, self)

    def status(self, code: int) -> R:
        """
        Set HTTP status code for response.

        Parameters:
            code: HTTP status code (e.g., 200, 404, 500)

        Returns:
            Self for method chaining
        """
        self.status = code
        return cast(R, self)

    def header(self, name: str, value: str) -> R:
        """
        Add or replace HTTP header in response.

        Parameters:
            name: Header name
            value: Header value

        Returns:
            Self for method chaining
        """
        self.headers[name] = value
        return cast(R, self)