from http.cookies import SimpleCookie
from typing import Optional


class Sessions:
    """
    A class for managing HTTP cookies using SimpleCookie.

    This class allows you to add, retrieve, update, and remove cookies.
    """

    def __init__(self) -> None:
        """Initialize with SimpleCookie to manage cookies."""
        self.cookies = SimpleCookie()  # Storage for cookies

    def add(self, name: str, value: str, path: str = "/", secure: bool = False, expires: Optional[int] = None) -> None:
        """
        Add a new cookie to the SimpleCookie storage.

        Args:
            name (str): The name of the cookie.
            value (str): The value of the cookie.
            path (str): The path for the cookie (default is "/").
            secure (bool): Whether the cookie requires a secure connection.
            expires (Optional[int]): Expiration time for the cookie in seconds.
        """
        # Create a new cookie
        self.cookies[name] = value
        self.cookies[name]['path'] = path
        if secure:
            self.cookies[name]['secure'] = True
        if expires:
            self.cookies[name]['expires'] = expires

    def get(self, name: str) -> Optional[str]:
        """
        Retrieve the value of a cookie by its name.

        Args:
            name (str): The name of the cookie.

        Returns:
            Optional[str]: The value of the cookie if found, otherwise None.
        """
        # Return the value of the cookie if it exists
        if name in self.cookies:
            return self.cookies[name].value
        return None

    def update(self, name: str, value: str) -> bool:
        """
        Update an existing cookie's value.

        Args:
            name (str): The name of the cookie.
            value (str): The new value for the cookie.

        Returns:
            bool: True if the cookie was found and updated, False if not.
        """
        # Check if the cookie exists and update its value
        if name in self.cookies:
            self.cookies[name] = value
            return True
        return False

    def remove(self, name: str) -> bool:
        """
        Remove a cookie by its name.

        Args:
            name (str): The name of the cookie to remove.

        Returns:
            bool: True if the cookie was found and removed, False if not.
        """
        # Remove the cookie if it exists
        if name in self.cookies:
            del self.cookies[name]
            return True
        return False

    def all(self) -> dict:
        """
        Retrieve all cookies as a dictionary of name-value pairs.

        Returns:
            dict: All cookies in the form {name: value}.
        """
        # Return all cookies as a dictionary
        return {key: morsel.value for key, morsel in self.cookies.items()}
