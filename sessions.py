from http.cookies import SimpleCookie
from typing import Optional, Dict, List, Union
import time
from urllib.parse import quote, unquote


class Sessions:
    """
    A comprehensive class for managing HTTP cookies using SimpleCookie.
    This class provides a convenient interface for adding, retrieving, updating,
    and removing HTTP cookies, which are commonly used for session management,
    user preferences, and other client-side storage needs.
    """

    def __init__(self) -> None:
        """
        Initialize the Sessions class with an empty SimpleCookie object.

        This constructor creates a new instance of the Sessions class with a fresh
        SimpleCookie container that will store all cookie information.
        """
        self.cookies = SimpleCookie()

    def add(
            self,
            cookie: Union[str, Dict[str, str]],
            value: Optional[str] = None,
            path: str = "/",
            domain: Optional[str] = None,
            secure: bool = False,
            httponly: bool = False,
            onsite: Optional[str] = None,
            expires: Optional[int] = None,
            longevity: Optional[int] = None,
    ) -> Union[None, Dict[str, bool]]:
        """
        Add a new cookie or multiple cookies to the SimpleCookie storage.

        This method allows adding cookies with various attributes such as path, domain,
        security settings, and expiration details. It can handle either a single cookie
        or multiple cookies through a dictionary.

        Args:
            cookie (Union[str, Dict[str, str]]): The name of the cookie or a dictionary of cookie names and values.
            value (Optional[str]): The value to assign to the cookie (required if `cookie` is a string).
            path (str): The URL path for which the cookie is valid. Defaults to "/".
            domain (Optional[str]): The domain for which the cookie is valid.
            secure (bool): Whether the cookie should only be transmitted over HTTPS.
            httponly (bool): Whether the cookie should be accessible only through HTTP.
            onsite (Optional[str]): Controls whether the cookie is sent with cross-site requests.
            expires (Optional[int]): Expiration time for the cookie in seconds from the current time.
            longevity (Optional[int]): Maximum age of the cookie in seconds.

        Returns:
            Union[None, Dict[str, bool]]: None if adding a single cookie, or a dictionary of cookie names and success statuses if adding multiple cookies.

        Raises:
            ValueError: If no value is provided when adding a single cookie or if an invalid onsite value is specified.
        """
        if isinstance(cookie, dict):
            results = {}
            for name, value in cookie.items():
                self.cookies[name] = quote(value)
                self.cookies[name]["path"] = path

                if domain:
                    self.cookies[name]["domain"] = domain
                if secure:
                    self.cookies[name]["secure"] = True
                if httponly:
                    self.cookies[name]["httponly"] = True
                if onsite:
                    rules = ["Strict", "Lax", "None"]
                    if onsite in rules:
                        self.cookies[name]["onsite"] = onsite
                    else:
                        raise ValueError(f"Invalid onsite value: {onsite}. Must be one of {rules}")
                if expires:
                    expiration = time.time() + expires
                    self.cookies[name]["expires"] = time.strftime(
                        "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expiration))
                if longevity:
                    self.cookies[name]["longevity"] = str(longevity)

                results[name] = True
            return results
        else:
            if value is None:
                raise ValueError("Value must be provided when adding a single cookie.")
            self.cookies[cookie] = quote(value)
            self.cookies[cookie]["path"] = path

            if domain:
                self.cookies[cookie]["domain"] = domain
            if secure:
                self.cookies[cookie]["secure"] = True
            if httponly:
                self.cookies[cookie]["httponly"] = True
            if onsite:
                rules = ["Strict", "Lax", "None"]
                if onsite in rules:
                    self.cookies[cookie]["onsite"] = onsite
                else:
                    raise ValueError(f"Invalid samesit value: {onsite}. Must be one of {rules}")
            if expires:
                expiration = time.time() + expires
                self.cookies[cookie]["expires"] = time.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expiration))
            if longevity:
                self.cookies[cookie]["longevity"] = str(longevity)

    def get(self, cookie: Union[str, List[str]], default: Optional[str] = None) -> Union[
        Optional[str], Dict[str, Optional[str]]]:
        """
        Retrieve the value of a cookie or multiple cookies.

        This method allows fetching the values of cookies from the storage. It can
        retrieve either a single cookie value or multiple cookie values, with support
        for a default return value if a cookie doesn't exist.

        Args:
            cookie (Union[str, List[str]]): The name of the cookie or a list of cookie names.
            default (Optional[str]): The value to return if the cookie is not found.

        Returns:
            Union[Optional[str], Dict[str, Optional[str]]]: The value of the cookie if a single cookie is requested,
            or a dictionary of cookie names and values if multiple cookies are requested.
        """
        if isinstance(cookie, list):
            results = {}
            for name in cookie:
                results[name] = self.get(name, default)
            return results
        else:
            if cookie in self.cookies:
                return unquote(self.cookies[cookie].value)
            return default

    def update(
            self,
            cookie: Union[str, Dict[str, str]],
            value: Optional[str] = None,
            attributes: bool = True,
    ) -> Union[bool, Dict[str, bool]]:
        """
        Update an existing cookie's value or multiple cookies' values.

        This method modifies the value of cookies that already exist in the storage.
        It can update either a single cookie or multiple cookies at once. When updating,
        you can choose whether to preserve the existing cookie attributes.

        Args:
            cookie (Union[str, Dict[str, str]]): The name of the cookie or a dictionary of cookie names and values.
            value (Optional[str]): The new value to assign to the cookie (required if `cookie` is a string).
            attributes (bool): Whether to preserve existing cookie attributes.

        Returns:
            Union[bool, Dict[str, bool]]]: True if the cookie was found and updated, or a dictionary of cookie names and success statuses if updating multiple cookies.

        Raises:
            ValueError: If no value is provided when updating a single cookie.
        """
        if isinstance(cookie, dict):
            results = {}
            for name, value in cookie.items():
                results[name] = self.update(name, value, attributes)
            return results
        else:
            if value is None:
                raise ValueError("Value must be provided when updating a single cookie.")
            if cookie in self.cookies:
                if attributes:
                    attribute = {key: value for key, value in self.cookies[cookie].items() if key != "value"}
                    self.cookies[cookie] = quote(value)
                    for key, value in attribute.items():
                        self.cookies[cookie][key] = value
                else:
                    self.cookies[cookie] = quote(value)
                return True
            return False

    def remove(self, cookie: Union[str, List[str]]) -> Union[bool, Dict[str, bool]]:
        """
        Remove a cookie or multiple cookies from the internal storage.

        This method deletes cookies from the internal storage. It doesn't affect cookies
        already set on the client side - use the expire() method for that purpose.
        It can remove either a single cookie or multiple cookies at once.

        Args:
            cookie (Union[str, List[str]]): The name of the cookie or a list of cookie names.

        Returns:
            Union[bool, Dict[str, bool]]]: True if the cookie was found and removed, or a dictionary of cookie names and removal statuses if removing multiple cookies.
        """
        if isinstance(cookie, list):
            results = {}
            for name in cookie:
                results[name] = self.remove(name)
            return results
        else:
            if cookie in self.cookies:
                del self.cookies[cookie]
                return True
            return False

    def expire(self, cookie: Union[str, List[str]], path: str = "/", domain: Optional[str] = None) -> Union[
        bool, Dict[str, bool]]:
        """
        Expire a cookie or multiple cookies on the client side.

        This method sets cookies to expire immediately, effectively removing them
        from the client browser. It does this by setting the cookies' expiration date
        to a past date and the max-age attribute to 0. This method is useful for
        logging users out or clearing sensitive information.

        Args:
            cookie (Union[str, List[str]]): The name of the cookie or a list of cookie names.
            path (str): The path of the cookies to expire.
            domain (Optional[str]): The domain of the cookies to expire.

        Returns:
            Union[bool, Dict[str, bool]]: True if the operation was successful, or a dictionary of cookie names and expiration statuses if expiring multiple cookies.
        """
        if isinstance(cookie, list):
            results = {}
            for name in cookie:
                results[name] = self.expire(name, path, domain)
            return results
        else:
            self.cookies[cookie] = ""
            self.cookies[cookie]["path"] = path
            if domain:
                self.cookies[cookie]["domain"] = domain
            self.cookies[cookie]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
            self.cookies[cookie]["max-age"] = "0"
            return True

    def all(self) -> Dict[str, str]:
        """
        Retrieve all cookies as a dictionary of name-value pairs.

        This method provides a convenient way to get all cookies currently stored in
        the Sessions object as a simple dictionary, with cookie names as keys and
        cookie values as the corresponding values.

        Returns:
            Dict[str, str]: A dictionary containing all cookie names and their values.
        """
        return {key: unquote(morsel.value) for key, morsel in self.cookies.items()}

    def exists(self, cookie: str) -> bool:
        """
        Check if a cookie exists in the storage.

        This method determines whether a specific cookie is present in the internal
        storage, regardless of its value.

        Args:
            cookie (str): The name of the cookie to check.

        Returns:
            bool: True if the cookie exists, False otherwise.
        """
        return cookie in self.cookies

    def headers(self) -> str:
        """
        Get the complete Set-Cookie header string.

        This method generates the HTTP header string for setting all cookies currently
        in the Sessions object. The resulting string can be directly included in HTTP
        response headers.

        Returns:
            str: The Set-Cookie HTTP header string.
        """
        return self.cookies.output(header="", sep="\r\nSet-Cookie: ")

    def attributes(self, cookie: str) -> Dict[str, str]:
        """
        Get a cookie with all its attributes.

        This method retrieves all attributes of a specific cookie, including its value
        and any other properties like path, domain, expiration, etc. It's useful for
        inspecting the full configuration of a cookie.

        Args:
            cookie (str): The name of the cookie to get attributes for.

        Returns:
            Dict[str, str]: A dictionary containing all attributes of the cookie, or an empty dictionary if the cookie doesn't exist.
        """
        if cookie not in self.cookies:
            return {}
        morsel = self.cookies[cookie]
        attributes = {"value": unquote(morsel.value)}
        for key, value in morsel.items():
            if key != "value":
                attributes[key] = value
        return attributes