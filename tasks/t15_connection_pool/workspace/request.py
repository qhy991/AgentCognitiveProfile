"""HTTP request representation."""


class Request:
    """A simple HTTP request object."""

    def __init__(self, method, url, json=None, headers=None):
        self.method = method.upper()
        self.url = url
        self.json = json
        self.headers = headers or {}

    def __repr__(self):
        return f"Request({self.method} {self.url})"