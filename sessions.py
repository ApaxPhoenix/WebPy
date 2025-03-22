from http.cookies import SimpleCookie
from typing import Optional, Dict, List, Union
import time
from urllib.parse import quote, unquote


class Sessions:
    """
    Cookie management system for HTTP session handling.

    Provides a comprehensive interface for managing browser cookies with support
    for creating, reading, updating, and deleting cookies with fine-grained control
    over security attributes, expiration, and cross-site behavior.

    The Sessions class abstracts away the complexity of cookie handling while
    enforcing best practices for secure cookie management in web applications.
    """

    def __init__(self) -> None:
        """
        Initialize a new cookie management instance.

        Creates an empty SimpleCookie container that will store and track
        all cookie operations throughout the application lifecycle.
        """
        self.container = SimpleCookie()

    def add(
            self,
            identity: Union[str, Dict[str, str]],
            value: Optional[str] = None,
            path: str = "/",
            domain: Optional[str] = None,
            secure: bool = False,
            httponly: bool = False,
            samesite: Optional[str] = None,
            expires: Optional[int] = None,
            maxage: Optional[int] = None,
    ) -> Union[None, Dict[str, bool]]:
        """
        Create new cookie(s) with specified attributes.

        Adds one or multiple cookies to the session management system with
        configurable security features and expiration settings. Supports both
        individual and bulk cookie creation.

        Parameters:
            identity: Cookie name or dictionary of cookie name-value pairs
            value: Cookie value (required when identity is a string)
            path: URL path scope for the cookie (defaults to root path)
            domain: Domain scope for the cookie
            secure: Restrict cookie to HTTPS connections only
            httponly: Prevent JavaScript access to the cookie
            samesite: Cross-site request policy ("Strict", "Lax", or "None")
            expires: Seconds from now until cookie expiration
            maxage: Maximum cookie lifetime in seconds

        Returns:
            None for single cookie creation, or dictionary of success statuses
            for bulk cookie creation

        Raises:
            ValueError: When missing value for single cookie or invalid samesite value
        """
        if isinstance(identity, dict):
            results = {}
            for name, content in identity.items():
                self.container[name] = quote(content)
                self.container[name]["path"] = path

                if domain:
                    self.container[name]["domain"] = domain
                if secure:
                    self.container[name]["secure"] = True
                if httponly:
                    self.container[name]["httponly"] = True

                if samesite:
                    policies = ["Strict", "Lax", "None"]
                    if samesite in policies:
                        self.container[name]["samesite"] = samesite
                    else:
                        raise ValueError(f"Invalid samesite value: {samesite}. Must be one of {policies}")

                if expires:
                    expiration = time.time() + expires
                    self.container[name]["expires"] = time.strftime(
                        "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expiration))

                if maxage:
                    self.container[name]["max-age"] = str(maxage)

                results[name] = True
            return results
        else:
            if value is None:
                raise ValueError("Value must be provided when adding a single cookie.")

            self.container[identity] = quote(value)
            self.container[identity]["path"] = path

            if domain:
                self.container[identity]["domain"] = domain
            if secure:
                self.container[identity]["secure"] = True
            if httponly:
                self.container[identity]["httponly"] = True

            if samesite:
                policies = ["Strict", "Lax", "None"]
                if samesite in policies:
                    self.container[identity]["samesite"] = samesite
                else:
                    raise ValueError(f"Invalid samesite value: {samesite}. Must be one of {policies}")

            if expires:
                expiration = time.time() + expires
                self.container[identity]["expires"] = time.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expiration))

            if maxage:
                self.container[identity]["max-age"] = str(maxage)

    def get(self, identity: Union[str, List[str]], default: Optional[str] = None) -> Union[
        Optional[str], Dict[str, Optional[str]]]:
        """
        Retrieve cookie value(s) from the session.

        Extracts the value of one or multiple cookies, with support for
        default values when cookies don't exist.

        Parameters:
            identity: Cookie name or list of cookie names to retrieve
            default: Fallback value when cookie doesn't exist

        Returns:
            Single cookie value or dictionary of cookie values mapped by name
        """
        if isinstance(identity, list):
            results = {}
            for name in identity:
                results[name] = self.get(name, default)
            return results
        else:
            if identity in self.container:
                return unquote(self.container[identity].value)
            return default

    def update(
            self,
            identity: Union[str, Dict[str, str]],
            value: Optional[str] = None,
            preserve: bool = True,
    ) -> Union[bool, Dict[str, bool]]:
        """
        Modify existing cookie value(s) with option to retain attributes.

        Updates one or multiple cookies that already exist in the session,
        with the choice to preserve or reset existing cookie attributes.

        Parameters:
            identity: Cookie name or dictionary of cookie name-value pairs
            value: New cookie value (required when identity is a string)
            preserve: Whether to maintain existing cookie attributes

        Returns:
            Success status for single update or dictionary of success statuses

        Raises:
            ValueError: When missing value for single cookie update
        """
        if isinstance(identity, dict):
            results = {}
            for name, content in identity.items():
                results[name] = self.update(name, content, preserve)
            return results
        else:
            if value is None:
                raise ValueError("Value must be provided when updating a single cookie.")

            if identity in self.container:
                if preserve:
                    properties = {key: val for key, val in self.container[identity].items() if key != "value"}
                    self.container[identity] = quote(value)
                    for key, val in properties.items():
                        self.container[identity][key] = val
                else:
                    self.container[identity] = quote(value)
                return True
            return False

    def remove(self, identity: Union[str, List[str]]) -> Union[bool, Dict[str, bool]]:
        """
        Delete cookie(s) from the session container.

        Removes one or multiple cookies from internal tracking, without
        affecting cookies already set on the client side.

        Parameters:
            identity: Cookie name or list of cookie names to remove

        Returns:
            Success status for single removal or dictionary of success statuses
        """
        if isinstance(identity, list):
            results = {}
            for name in identity:
                results[name] = self.remove(name)
            return results
        else:
            if identity in self.container:
                del self.container[identity]
                return True
            return False

    def expire(self, identity: Union[str, List[str]], path: str = "/", domain: Optional[str] = None) -> Union[
        bool, Dict[str, bool]]:
        """
        Force cookie expiration on the client browser.

        Sets cookies to expire immediately by setting expiration date
        to the past and max-age to zero, effectively removing them from
        the client browser on the next response.

        Parameters:
            identity: Cookie name or list of cookie names to expire
            path: Path scope matching the cookies to expire
            domain: Domain scope matching the cookies to expire

        Returns:
            Success status for single expiration or dictionary of success statuses
        """
        if isinstance(identity, list):
            results = {}
            for name in identity:
                results[name] = self.expire(name, path, domain)
            return results
        else:
            self.container[identity] = ""
            self.container[identity]["path"] = path

            if domain:
                self.container[identity]["domain"] = domain

            # Set expiration to the past (Unix epoch)
            self.container[identity]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"

            # Set max-age to zero for immediate expiration
            self.container[identity]["max-age"] = "0"

            return True

    def all(self) -> Dict[str, str]:
        """
        Retrieve all cookie values as a simple dictionary.

        Provides a straightforward name-value mapping of all cookies
        currently managed by the session, with values properly decoded.

        Returns:
            Dictionary of all cookie names and their decoded values
        """
        return {name: unquote(morsel.value) for name, morsel in self.container.items()}

    def exists(self, identity: str) -> bool:
        """
        Check for cookie existence in the session.

        Determines whether a specific cookie is present in the
        session container, regardless of its value.

        Parameters:
            identity: Cookie name to check

        Returns:
            True if cookie exists, False otherwise
        """
        return identity in self.container

    def headers(self) -> str:
        """
        Generate complete Set-Cookie HTTP header string.

        Creates properly formatted HTTP headers for setting all
        cookies currently in the session container, ready for
        inclusion in HTTP responses.

        Returns:
            Complete Set-Cookie header string for HTTP response
        """
        return self.container.output(header="", sep="\r\nSet-Cookie: ")

    def attributes(self, identity: str) -> Dict[str, str]:
        """
        Extract all properties of a specific cookie.

        Retrieves the complete configuration of a cookie including
        its value and all security attributes, expiration settings,
        and other properties.

        Parameters:
            identity: Cookie name to inspect

        Returns:
            Dictionary of all cookie attributes or empty dict if cookie not found
        """
        if identity not in self.container:
            return {}

        morsel = self.container[identity]
        properties = {"value": unquote(morsel.value)}

        # Add all non-value attributes
        for key, val in morsel.items():
            if key != "value":
                properties[key] = val

        return properties