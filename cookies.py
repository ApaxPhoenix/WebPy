import http.cookies


class Cookies:
    def __init__(self, request=None, response=None):
        self.request = request
        self.response = response

    def set_cookie(self, key, value, max_age=None, expires=None, path='/', domain=None, secure=False, httponly=False):
        """
        Set a cookie in the response headers.

        Args:
            key: The name of the cookie.
            value: The value of the cookie.
            max_age (int, optional): The maximum age of the cookie in seconds.
            expires (datetime, optional): The expiration date and time of the cookie.
            path (str, optional): The path for which the cookie is valid.
            domain (str, optional): The domain for which the cookie is valid.
            secure (bool, optional): Whether the cookie should only be sent over secure connections.
            httponly (bool, optional): Whether the cookie should be accessible only through HTTP requests.
        """
        cookie = http.cookies.SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]['max-age'] = max_age
        if expires is not None:
            cookie[key]['expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        cookie[key]['path'] = path
        if domain is not None:
            cookie[key]['domain'] = domain
        if secure:
            cookie[key]['secure'] = secure
        if httponly:
            cookie[key]['httponly'] = httponly

        if self.response:
            self.response.headers['Set-Cookie'] = cookie.output(header='')

    def get_cookie(self, key):
        """
        Get the value of a cookie by its key.

        Args:
            key (str): The name of the cookie.

        Returns:
            str: The value of the cookie, or None if not found.
        """
        if self.request:
            cookies = http.cookies.SimpleCookie(self.request.headers.get('Cookie', ''))
            return cookies.get(key)
        else:
            return None

    def delete_cookie(self, key):
        self.set_cookie(key, '', expires=0)
