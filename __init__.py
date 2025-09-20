from .core import WebPyCore
from .router import Router
from .broadcast import Request, Response
from .middleware import Middleware
from .sessions import Sessions
from .blueprint import Blueprint

# Export the main classes and components
__all__ = [
    "WebPyCore",  # The core application class
    "Router",  # The router for handling routes
    "Request",  # The request object for handling incoming requests
    "Response",  # The response object for sending responses
    "Middleware",  # The middleware system for request/response processing
    "Sessions",  # The session management system
    "Blueprint",  # The blueprint system for modular applications
]

# Package metadata
__version__ = "0.1.0"
__author__ = "Andrew Hernandez"
__license__ = "MIT"
__description__ = "A modern, lightweight Python web framework for building scalable web applications with intuitive routing, flexible middleware, session management, and minimal boilerplate code."
__url__ = "https://github.com/ApaxPhoenix/WebPy"
__email__ = "andromedeyz@hotmail.com"

# HTTP status codes - what the server is telling you
codes = {
    # 1xx - Informational responses
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",

    # 2xx - Success
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",

    # 3xx - Redirection
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",

    # 4xx - Client errors
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",

    # 5xx - Server errors
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
}

# MIME types for file extensions
mimes = {
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".txt": "text/plain",
    ".json": "application/json",
    ".xml": "application/xml",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".eot": "application/vnd.ms-fontobject",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".csv": "text/csv",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    ".toml": "application/toml",
    ".md": "text/markdown",
    ".rtf": "application/rtf",
}

# Python version compatibility enforcement
import sys

if sys.version_info < (3, 9):
    raise RuntimeError("WebPy requires Python 3.9 or higher")