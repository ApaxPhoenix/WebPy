from typing import Any, Dict, TypeVar, Union, List, Set
import re

T = TypeVar('T')
DataType = Union[str, Dict[str, Any], List[Any]]


class XSS:
    """
    Cross-Site Scripting (XSS) protection module that implements comprehensive
    sanitization of user inputs to prevent malicious script injection in web applications.

    This module provides both character-based sanitization and pattern recognition to
    detect and neutralize common XSS attack vectors through middleware integration.
    """

    def __init__(self, app: Any) -> None:
        """
        Initializes the XSS protection module and configures the middleware
        to intercept and sanitize user inputs before request processing.

        Args:
            app: The web application instance to protect against XSS attacks
        """
        self.app = app

        # Comprehensive HTML entity map for character replacement during sanitization
        self.entities: Dict[str, str] = {
            # Basic HTML entities
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;',

            # Extended protection for script execution prevention
            '/': '&#x2F;', '`': '&#x60;', '=': '&#x3D;', '{': '&#x7B;', '}': '&#x7D;',
            '(': '&#x28;', ')': '&#x29;', '%': '&#x25;', '#': '&#x23;', ';': '&#x3B;',

            # Additional protections for JS event handlers and CSS injections
            '\\': '&#x5C;', '|': '&#x7C;', '[': '&#x5B;', ']': '&#x5D;', '^': '&#x5E;',
            '*': '&#x2A;', '+': '&#x2B;', '?': '&#x3F;', '!': '&#x21;', '@': '&#x40;',
            '$': '&#x24;', '~': '&#x7E;', ':': '&#x3A;', ',': '&#x2C;'
        }

        # Dangerous patterns that might indicate XSS attempts
        self.patterns: List[str] = [
            r'javascript\s*:',
            r'data\s*:',
            r'vbscript\s*:',
            r'expression\s*\(',
            r'document\.cookie',
            r'document\.location',
            r'document\.write',
            r'window\.location',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'on\w+\s*=',  # Matches event handlers like onclick, onload
            r'<script[^>]*>',
            r'<iframe[^>]*>',
            r'<img[^>]*\s+onerror\s*=',
            r'url\s*\(',  # CSS url injection
        ]

        # Compile patterns for performance
        self.cache: List[re.Pattern] = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.patterns
        ]

        # Protected request attributes that should be sanitized
        self.fields: Set[str] = {'params', 'form', 'query', 'json', 'cookies', 'headers'}

        # Register middleware hook to process incoming requests
        @app.before
        def process(request: Any, response: Any) -> bool:
            """
            Intercepts and sanitizes all potential user input vectors to prevent XSS attacks.

            Args:
                request: The incoming request object containing user data
                response: The response object (unused but required by middleware interface)

            Returns:
                True to continue request processing, False to abort
            """
            for field in self.fields:
                if hasattr(request, field):
                    data = getattr(request, field)
                    if data:
                        clean = self.sanitize(data)
                        setattr(request, field, clean)
            return True

    def sanitize(self, value: DataType) -> DataType:
        """
        Recursively sanitizes input by replacing dangerous characters with HTML entities
        and detecting potentially malicious patterns.

        Args:
            value: The input value to sanitize (string, dict, list, or other types)

        Returns:
            Sanitized version of the input with potentially dangerous content neutralized
        """
        # Process string inputs
        if isinstance(value, str):
            text = value

            # Replace dangerous characters with HTML entities
            for char, entity in self.entities.items():
                text = text.replace(char, entity)

            # Check for malicious patterns and neutralize them
            for rule in self.cache:
                text = rule.sub('', text)

            return text

        # Recursively process dictionary inputs
        elif isinstance(value, dict):
            return {key: self.sanitize(item) for key, item in value.items()}

        # Recursively process list inputs
        elif isinstance(value, list):
            return [self.sanitize(item) for item in value]

        # Return other types unchanged
        return value

    def add(self, pattern: str) -> None:
        """
        Adds a custom regex pattern to detect additional malicious content.

        Args:
            pattern: Regular expression pattern to identify potentially malicious content
        """
        self.patterns.append(pattern)
        self.cache.append(re.compile(pattern, re.IGNORECASE))

    def watch(self, field: str) -> None:
        """
        Adds a custom request attribute to the protection list.

        Args:
            field: Name of the request attribute to sanitize
        """
        self.fields.add(field)