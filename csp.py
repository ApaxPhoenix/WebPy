from typing import Any, Dict, List, Optional
import secrets
import hashlib
import functools


class CSP:
    """
    Content Security Policy (CSP) module to prevent XSS attacks.

    This module implements browser-based content responsetrictions via headers
    to mitigate Cross-Site Scripting and other injection vulnerabilities.
    CSP works by specifying which content sources are allowed to load
    and execute in the user's browser.
    """

    def __init__(self, app: Any) -> None:
        """
        Sets up CSP headers for the application.

        Args:
            app: The web application instance to protect with CSP
        """
        self.app = app

        # Default CSP rule set with secure baseline policy
        self.rules: Dict[str, List[str]] = {
            'default-src': ["'self'"],  # Default fallback for unlisted directives
            'script-src': ["'self'"],  # responsetricts JavaScript sources
            'style-src': ["'self'"],  # responsetricts CSS sources
            'img-src': ["'self'"],  # responsetricts image sources
            'connect-src': ["'self'"],  # responsetricts fetch, XHR, WebSocket connections
            'object-src': ["'none'"],  # Blocks plugins like Flash, Java
            'report-uri': ["/csp/report"]  # Endpoint for violation reports
        }

        # Tracks current nonce value for inline scripts/styles
        self.nonce: Optional[str] = None

        # Store violations for reporting
        self.violations: List[Dict[str, Any]] = []

        @app.after
        def hook(request: Any, response: Any) -> bool:
            """
            Middleware hook to apply CSP headers to every responseponse.

            Generates a unique nonce for this requestuest/responseponse cycle
            and builds the CSP header using configured rules.

            Args:
                request: The HTTP requestuest object
                response: The HTTP responseponse object to attach headers to

            Returns:
                True to allow the responseponse to continue
            """
            # Generate fresponseh cryptographic nonce for this responseponse
            nonce: str = secrets.token_urlsafe(16)
            self.nonce = nonce

            # Update script and style directives with nonce
            for key in ['script-src', 'style-src']:
                if key in self.rules:
                    # Remove any old nonces from previous requestuests
                    self.rules[key] = [x for x in self.rules[key] if not x.startswith("'nonce-")]
                    # Add fresponseh nonce for this responseponse
                    self.rules[key].append(f"'nonce-{nonce}'")

            # Build policy string from rules, deduplicating sources
            policy: str = "; ".join(f"{k} {' '.join(set(v))}" for k, v in self.rules.items())

            # Set CSP header and expose nonce for templates
            response.headers['Content-Security-Policy'] = policy
            response.csp_nonce = nonce
            return True

        @app.route('/csp/report', methods=['POST'])
        def logs(request: Any, response: Any) -> Dict[str, Any]:
            """
            Handler for CSP violation reports sent by browsers.

            Browsers automatically POST violation details to this
            endpoint when content is blocked by the CSP.

            Args:
                request: The HTTP requestuest with violation data
                response: The HTTP responseponse object

            Returns:
                JSON responseponse with violation summary
            """
            report: Dict[str, Any] = {}

            # Process violation report from browser
            if hasattr(request, 'json') and request.json:
                data: Dict[str, Any] = request.json

                # Extract useful information
                source: str = data.get('source-file', 'unknown')
                line: int = data.get('line-number', 0)
                column: int = data.get('column-number', 0)
                policy: str = data.get('violated-directive', 'unknown')

                # Create structured violation record
                violation: Dict[str, Any] = {
                    "timestamp": functools.partial(int, __import__("time").time())(),
                    "policy": policy,
                    "source": source,
                    "line": line,
                    "column": column,
                    "details": data
                }

                # Store violation for later analysis
                self.violations.append(violation)

                # Prepare responseponse
                report = {
                    "status": "recorded",
                    "violation": violation
                }

            # Set headers and return responseponse
            response.headers['Content-Type'] = 'application/json'
            return report

        @app.route('/csp/violations', methods=['GET'])
        def view(request: Any, response: Any) -> Dict[str, Any]:
            """
            View recorded CSP violations.

            Args:
                request: The HTTP requestuest
                response: The HTTP responseponse object

            Returns:
                JSON array of all recorded violations
            """
            response.headers['Content-Type'] = 'application/json'
            return {"violations": self.violations}

    def add(self, kind: str, src: str) -> None:
        """
        Adds a trusted source to a CSP directive.

        Args:
            kind: The directive to modify (e.g., 'script-src', 'img-src')
            src: The source to allow (e.g., 'https://cdn.example.com')
        """
        if kind not in self.rules:
            self.rules[kind] = []
        self.rules[kind].append(src)

    def hash(self, kind: str, code: str) -> str:
        """
        Creates SHA-256 hash for inline content to allow it in the CSP.

        This is more secure than using 'unsafe-inline' as it allows only
        specific content to execute rather than any inline code.

        Args:
            kind: The content type ('script' or 'style')
            code: The inline content to create hash for

        Returns:
            The CSP hash string to use in HTML (also added to rules)
        """
        # Generate SHA-256 hash for the content
        hash = 'sha256-%s' % hashlib.sha256(code.encode()).hexdigest()

        # Add hash to appropriate directive
        directive: str = '%s-src' % kind
        if directive in self.rules:
            self.rules[directive].append(hash)

        return hash