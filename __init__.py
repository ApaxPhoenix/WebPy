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

# Python version compatibility enforcement
import sys

if sys.version_info < (3, 9):
    raise RuntimeError("WebPy requires Python 3.9 or higher")
