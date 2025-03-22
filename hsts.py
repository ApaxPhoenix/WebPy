from typing import Any, Dict, Optional


class HSTS:
    """
    HTTP Strict Transport Security (HSTS) module.

    Enforces secure connections by instructing browsers
    to only use HTTPS for the website.

    HSTS protects against protocol downgrade attacks and
    cookie hijacking by telling browsers to only use HTTPS.
    """

    def __init__(self, app: Any) -> None:
        """
        Sets up HSTS headers for the application.

        Args:
            app: The web application instance to protect with HSTS
        """
        self.app = app

        # Default HSTS settings
        self.longevity: int = 52 * 7 * 24 * 60 * 60  # 1 year in seconds
        self.subdomains: bool = True
        self.preload: bool = False

        @app.after
        def hook(request: Any, response: Any) -> bool:
            """
            Middleware hook to apply HSTS headers to every response.

            Args:
                request: The HTTP request object
                response: The HTTP response object to attach headers to

            Returns:
                True to allow the response to continue
            """
            # Check if the request is secure (over HTTPS)
            secure = False
            if hasattr(request, 'scheme'):
                secure = request.scheme == 'https'
            else:
                # Check for common proxy headers
                headers: Dict[str, str] = getattr(request, 'headers', {})
                forward: Optional[str] = headers.get('X-Forwarded-Proto')
                if forward:
                    secure = forward.lower() == 'https'

            # Skip HSTS for HTTP requests
            if not secure:
                return True

            # Build HSTS header value
            parts: list = [f"max-age={self.longevity}"]

            if self.subdomains:
                parts.append("includeSubDomains")

            if self.preload:
                parts.append("preload")

            header: str = "; ".join(parts)

            # Set HSTS header
            response.headers['Strict-Transport-Security'] = header
            return True

    def configuration(self, longevity: Optional[int] = None,
                      subdomains: Optional[bool] = None,
                      preload: Optional[bool] = None) -> None:
        """
        Configure HSTS settings.

        Args:
            longevity: Maximum time in seconds browsers should remember to use HTTPS
            subdomains: Whether to apply HSTS to all subdomains
            preload: Whether to allow inclusion in browser preload lists
        """
        if longevity is not None:
            self.longevity = longevity

        if subdomains is not None:
            self.subdomains = subdomains

        if preload is not None:
            self.preload = preload

    def enable(self, weeks: int = 52) -> None:
        """
        Enable HSTS with specified duration.

        Args:
            weeks: Number of weeks for max-age (default: 52 weeks/1 year)
        """
        self.longevity = weeks * 7 * 24 * 60 * 60  # Convert weeks to seconds

    def disable(self) -> None:
        """
        Disable HSTS by setting max-age to 0.

        This instructs browsers to stop enforcing HTTPS for future visits.
        """
        self.longevity = 0
