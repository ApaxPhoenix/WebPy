class PortInUseError(Exception):
    def __init__(self, port):
        self.port = port
        self.message = f"Port {port} is already in use."

    def __str__(self):
        return self.message


class MethodNotAllowedError(Exception):
    def __init__(self, method):
        self.method = method
        self.message = f"Method {method} is not allowed."

    def __str__(self):
        return self.message


class RouteNotFoundError(Exception):
    def __init__(self, path):
        self.path = path
        self.message = f"Route {path} not found."

    def __str__(self):
        return self.message


class APIRouteNotFoundError(Exception):
    def __init__(self, path):
        self.path = path
        self.message = f"API Route {path} not found."

    def __str__(self):
        return self.message


class UnsupportedMethodError(Exception):
    def __init__(self, method):
        super().__init__(f"Unsupported HTTP method: {method}")


class InvalidPathError(Exception):
    def __init__(self, path):
        super().__init__(f"Invalid path: {path}")


class InvalidQueryError(Exception):
    def __init__(self, query):
        super().__init__(f"Invalid query parameters: {query}")


class InvalidFragmentError(Exception):
    def __init__(self, fragment):
        super().__init__(f"Invalid fragment: {fragment}")


class InternalServerError(Exception):
    def __init__(self, message):
        super().__init__(f"Internal Server Error: {message}")
