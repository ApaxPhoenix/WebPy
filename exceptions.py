class PortInUseError(Exception):
    """
    Exception raised when a port is already in use.
    """
    def __init__(self, message):
        """
        Initialize a PortInUseError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class MethodNotAllowedError(Exception):
    """
    Exception raised when a method is not allowed.
    """
    def __init__(self, message):
        """
        Initialize a MethodNotAllowedError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class RouteNotFoundError(Exception):
    """
    Exception raised when a route is not found.
    """
    def __init__(self, message):
        """
        Initialize a RouteNotFoundError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class APIRouteNotFoundError(Exception):
    """
    Exception raised when an API route is not found.
    """
    def __init__(self, message):
        """
        Initialize an APIRouteNotFoundError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class UnsupportedMethodError(Exception):
    """
    Exception raised when an unsupported HTTP method is used.
    """
    def __init__(self, message):
        """
        Initialize an UnsupportedMethodError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class InvalidPathError(Exception):
    """
    Exception raised when an invalid path is provided.
    """
    def __init__(self, message):
        """
        Initialize an InvalidPathError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class InvalidQueryError(Exception):
    """
    Exception raised when invalid query parameters are provided.
    """
    def __init__(self, message):
        """
        Initialize an InvalidQueryError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class InvalidFragmentError(Exception):
    """
    Exception raised when an invalid fragment is provided.
    """
    def __init__(self, message):
        """
        Initialize an InvalidFragmentError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class InternalServerError(Exception):
    """
    Exception raised for internal server errors.
    """
    def __init__(self, message):
        """
        Initialize an InternalServerError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class RequestParsingError(Exception):
    """
    Exception raised when there is an error parsing the request.
    """
    def __init__(self, message):
        """
        Initialize a RequestParsingError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class JSONParsingError(Exception):
    """
    Exception raised when there is an error parsing JSON data from the request body.
    """
    def __init__(self, message):
        """
        Initialize a JSONParsingError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class ResponseSendingError(Exception):
    """
    Exception raised when there is an error sending the response.
    """
    def __init__(self, message):
        """
        Initialize a ResponseSendingError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message


class JSONResponseError(Exception):
    """
    Exception raised when there is an error setting the response body to JSON.
    """
    def __init__(self, message):
        """
        Initialize a JSONResponseError.

        Args:
            message (str): The error message.
        """
        self.message = message

    def __str__(self):
        """
        Return the error message as a string.

        Returns:
            str: Error message.
        """
        return self.message
    