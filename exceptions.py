class PortInUseError(Exception):
    def __init__(self, port):
        """
        Initialize a PortInUseError.

        Args:
            port (int): The port number that is already in use.
        """
        self.port = port
        self.message = f"Port {port} is already in use."

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class MethodNotAllowedError(Exception):
    def __init__(self, method):
        """
        Initialize a MethodNotAllowedError.

        Args:
            method (str): The HTTP method that is not allowed.
        """
        self.method = method
        self.message = f"Method {method} is not allowed."

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class RouteNotFoundError(Exception):
    def __init__(self, path):
        """
        Initialize a RouteNotFoundError.

        Args:
            path (str): The path that was not found.
        """
        self.path = path
        self.message = f"Route {path} not found."

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class APIRouteNotFoundError(Exception):
    def __init__(self, path):
        """
        Initialize an APIRouteNotFoundError.

        Args:
            path (str): The API route that was not found.
        """
        self.path = path
        self.message = f"API Route {path} not found."

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class UnsupportedMethodError(Exception):
    def __init__(self, method):
        """
        Initialize an UnsupportedMethodError.

        Args:
            method (str): The HTTP method that is not supported.
        """
        super().__init__(f"Unsupported HTTP method: {method}")


class InvalidPathError(Exception):
    def __init__(self, path):
        """
        Initialize an InvalidPathError.

        Args:
            path (str): The invalid path.
        """
        super().__init__(f"Invalid path: {path}")


class InvalidQueryError(Exception):
    def __init__(self, query):
        """
        Initialize an InvalidQueryError.

        Args:
            query (str): The invalid query parameters.
        """
        super().__init__(f"Invalid query parameters: {query}")


class InvalidFragmentError(Exception):
    def __init__(self, fragment):
        """
        Initialize an InvalidFragmentError.

        Args:
            fragment (str): The invalid fragment.
        """
        super().__init__(f"Invalid fragment: {fragment}")


class InternalServerError(Exception):
    def __init__(self, message):
        """
        Initialize an InternalServerError.

        Args:
            message (str): The error message.
        """
        super().__init__(f"Internal Server Error: {message}")
