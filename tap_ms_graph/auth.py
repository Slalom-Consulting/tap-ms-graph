"""Authentication classes for tap-ms-graph."""

from urllib.parse import urljoin

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

AUTH_URL = "https://login.microsoftonline.com"


class MSGraphAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for MSGraph."""

    @property
    def auth_endpoint(self) -> str:
        base = self.config.get("auth_url", AUTH_URL)
        tenant = self.config.get("tenant")
        endpoint = f"/{tenant}/oauth2/v2.0/token"
        return urljoin(base, endpoint)

    @property
    def oauth_request_body(self) -> dict:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "https://graph.microsoft.com/.default",
        }
