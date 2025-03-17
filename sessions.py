from http.cookies import SimpleCookie
from typing import Optional, Dict


class Sessions:
    """
    A class for managing HTTP cookies using SimpleCookie.

    This class provides a convenient interface for adding, retrieving, updating,
    and removing HTTP cookies, which are commonly used for session management,
    user preferences, and other client-side storage needs.
    """

    def __init__(self) -> None:
        """
        Initialize the Sessions class with an empty SimpleCookie object.

        Creates an internal SimpleCookie instance to store and manage HTTP cookies.
        """
        self.cookies = SimpleCookie()  # SimpleCookie instance for cookie management

    def add(
        self,
        cookie: str,
        value: str,
        path: str = "/",
        secure: bool = False,
        expires: Optional[int] = None,
    ) -> None:
        """
        Add a new cookie to the SimpleCookie storage.

        Creates a new cookie with the specified parameters and adds it to the
        internal cookie storage. This does not automatically send the cookie
        to the client; the cookie must be included in an HTTP response.

        Args:
            cookie (str): The name of the cookie to be set.
            value (str): The value to assign to the cookie.
            path (str): The URL path for which the cookie is valid. Defaults to "/",
                       making the cookie valid for the entire domain.
            secure (bool): Whether the cookie should only be transmitted over HTTPS.
                          Defaults to False.
            expires (Optional[int]): Expiration time for the cookie in seconds from
                                    the current time. If None, the cookie expires
                                    when the browser session ends.
        """
        # Create a new cookie with the specified value
        self.cookies[cookie] = value

        # Set the path attribute for the cookie
        self.cookies[cookie]["path"] = path

        # Set the secure flag if specified
        if secure:
            self.cookies[cookie]["secure"] = True

        # Set the expiration time if specified
        if expires:
            self.cookies[cookie]["expires"] = expires

    def get(self, cookie: str) -> Optional[str]:
        """
        Retrieve the value of a cookie by its name.

        Looks up the cookie in the internal storage and returns its value
        if found, or None if the cookie doesn't exist.

        Args:
            cookie (str): The name of the cookie to retrieve.

        Returns:
            Optional[str]: The value of the cookie if found, otherwise None.

        Example:
            user_id = sessions.get("user_id")
            if user_id:
                # Process user-specific logic
                pass
        """
        # Return the value of the cookie if it exists in storage
        if cookie in self.cookies:
            return self.cookies[cookie].value
        return None

    def update(self, cookie: str, value: str) -> bool:
        """
        Update an existing cookie's value.

        Finds the specified cookie in the internal storage and updates its
        value, preserving other attributes like path and expiration.

        Args:
            cookie (str): The name of the cookie to update.
            value (str): The new value to assign to the cookie.

        Returns:
            bool: True if the cookie was found and updated, False if the cookie
                 doesn't exist.

        Example:
            if sessions.update("theme", "dark"):
                # Cookie was successfully updated
                pass
        """
        # Check if the cookie exists and update its value if found
        if cookie in self.cookies:
            self.cookies[cookie] = value
            return True
        return False

    def remove(self, cookie: str) -> bool:
        """
        Remove a cookie from the internal storage.

        Deletes the specified cookie from the SimpleCookie object. To remove
        a cookie from the client's browser, you must also send a cookie with
        an expired date.

        Args:
            cookie (str): The name of the cookie to remove.

        Returns:
            bool: True if the cookie was found and removed, False if the cookie
                 doesn't exist.

        Example:
            if sessions.remove("temp_data"):
                # Cookie was successfully removed from storage
                pass
        """
        # Remove the cookie if it exists in storage
        if cookie in self.cookies:
            del self.cookies[cookie]
            return True
        return False

    def all(self) -> Dict[str, str]:
        """
        Retrieve all cookies as a dictionary of name-value pairs.

        Creates a dictionary representation of all cookies currently stored
        in the SimpleCookie object.

        Returns:
            Dict[str, str]: Dictionary containing all cookie names and their
                           corresponding values.

        Example:
            all_cookies = sessions.all()
            for name, value in all_cookies.items():
                print(f"Cookie {name}: {value}")
        """
        # Convert all cookies to a dictionary with name-value pairs
        return {key: morsel.value for key, morsel in self.cookies.items()}
