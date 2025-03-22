from .core import WebPyCore
from .router import Router
from .broadcast import Request, Response
from .middleware import Middleware
from .sessions import Sessions
from .blueprint import Blueprint

# Export the main classes and components
__all__ = [
    "WebPyCore",  # The core application class
    "Router",     # The router for handling routes
    "Request",    # The request object for handling incoming requests
    "Response",   # The response object for sending responses
    "Middleware", # The middleware system for request/response processing
    "Sessions",   # The session management system
    "Blueprint"   # The blueprint system for modular applications
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Andrew Hernandez"
__license__ = "MIT"
__description__ = "A lightweight web framework for handling requests and routing"
__url__ = "https://github.com/ApaxPhoenix/WebPy"
__email__ = "andromedeyz@hotmail.com"
