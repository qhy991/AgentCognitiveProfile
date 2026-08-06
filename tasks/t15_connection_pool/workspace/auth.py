"""Authentication provider for API requests."""


class AuthProvider:
    """Base class for authentication."""

    def get_header(self):
        """Return a dict of authentication headers."""
        raise NotImplementedError


class BearerAuth(AuthProvider):
    """Bearer token authentication."""

    def __init__(self, token):
        self.token = token

    def get_header(self):
        return {"Authorization": f"Bearer {self.token}"}


class BasicAuth(AuthProvider):
    """Basic authentication."""

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_header(self):
        import base64
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        return {"Authorization": f"Basic {credentials}"}