import logging
from typing import Optional, Tuple

import google_auth_oauthlib.flow
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Custom exception for application-level errors"""

    pass


class GoogleAccessToken:
    """Container for Google OAuth tokens"""

    def __init__(
        self, id_token: str, access_token: str, refresh_token: Optional[str] = None
    ):
        self.id_token = id_token
        self.access_token = access_token
        self.refresh_token = refresh_token


class GoogleCredentials:
    """Container for Google OAuth credentials"""

    def __init__(self, client_id: str, client_secret: str, project_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.project_id = project_id


def google_sdk_login_get_credentials() -> GoogleCredentials:
    """
    Retrieve Google OAuth credentials from Django settings.
    You need to implement this function or define these in your settings.
    """
    try:
        return GoogleCredentials(
            client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            project_id=settings.GOOGLE_OAUTH2_PROJECT_ID,
        )
    except AttributeError as e:
        raise ApplicationError(f"Missing Google OAuth configuration in settings: {e}")


class GoogleSdkLoginFlowService:
    """Service for handling Google OAuth 2.0 authentication flow"""

    # Google OAuth 2.0 endpoints
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"

    # OAuth scopes
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(self):
        self._credential = google_sdk_login_get_credentials()
        self._validate_settings()

    def _validate_settings(self):
        """Validate required settings are present"""
        if not hasattr(settings, "GOOGLE_OAUTH_REDIRECT_URI"):
            raise ApplicationError(
                "GOOGLE_OAUTH_REDIRECT_URI must be defined in Django settings"
            )

        if not self._credential.client_id or not self._credential.client_secret:
            raise ApplicationError(
                "Google OAuth client_id and client_secret must be configured"
            )

    def _get_redirect_uri(self) -> str:
        """
        Get the redirect URI for OAuth callback.
        This should match exactly what's registered in Google Cloud Console.
        """
        return settings.GOOGLE_OAUTH_REDIRECT_URI

    def _generate_client_config(self) -> dict:
        """Generate Google client configuration for oauth flow"""
        redirect_uri = self._get_redirect_uri()

        client_config = {
            "web": {
                "client_id": self._credential.client_id,
                "project_id": self._credential.project_id,
                "auth_uri": self.GOOGLE_AUTH_URL,
                "token_uri": self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL,
                "auth_provider_x509_cert_url": self.GOOGLE_AUTH_PROVIDER_CERT_URL,
                "client_secret": self._credential.client_secret,
                "redirect_uris": [redirect_uri],
            }
        }
        return client_config

    def get_authorization_url(self) -> Tuple[str, str]:
        """
        Generate Google authorization URL and state parameter.

        Returns:
            Tuple[str, str]: (authorization_url, state)
        """
        try:
            redirect_uri = self._get_redirect_uri()
            client_config = self._generate_client_config()

            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config=client_config,
                scopes=self.SCOPES,
            )
            flow.redirect_uri = redirect_uri

            # Generate authorization URL with PKCE and state parameter
            authorization_url, state = flow.authorization_url(
                access_type="offline",  # Request refresh token
                include_granted_scopes="true",
                prompt="select_account",  # Force account selection
            )

            logger.info(
                f"Generated Google authorization URL for redirect_uri: {redirect_uri}"
            )
            return authorization_url, state

        except Exception as exc:
            logger.error(f"Failed to generate authorization URL: {exc}")
            raise ApplicationError(
                f"Failed to generate authorization URL: {exc}"
            ) from exc

    def get_token(self, *, code: str, state: str) -> GoogleAccessToken:
        """
        Exchange authorization code for access tokens.

        Args:
            code: Authorization code from Google
            state: State parameter for CSRF protection

        Returns:
            GoogleAccessToken: Container with tokens
        """
        try:
            redirect_uri = self._get_redirect_uri()
            client_config = self._generate_client_config()

            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config=client_config,
                scopes=self.SCOPES,
                state=state,
            )
            flow.redirect_uri = redirect_uri

            # Exchange code for tokens
            token_resp = flow.fetch_token(code=code)

            if not token_resp or "access_token" not in token_resp:
                raise ApplicationError("Invalid token response from Google")

            logger.info("Successfully obtained tokens from Google")
            return GoogleAccessToken(
                id_token=token_resp.get("id_token", ""),
                access_token=token_resp["access_token"],
                refresh_token=token_resp.get("refresh_token"),
            )

        except Exception as exc:
            logger.error(f"Failed to obtain token from Google: {exc}")
            raise ApplicationError(
                f"Failed to obtain token from Google: {exc}"
            ) from exc

    def get_user_info(self, *, google_token: GoogleAccessToken) -> dict:
        """
        Retrieve user information using access token.

        Args:
            google_token: GoogleAccessToken instance

        Returns:
            dict: User information from Google
        """
        if not google_token.access_token:
            raise ApplicationError("Access token is required")

        headers = {
            "Authorization": f"Bearer {google_token.access_token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(
                self.GOOGLE_USER_INFO_URL, headers=headers, timeout=30
            )
            response.raise_for_status()  # Raises HTTPError for bad responses

            user_info = response.json()
            logger.info(
                f"Successfully retrieved user info for user: {user_info.get('email', 'unknown')}"
            )
            return user_info

        except requests.RequestException as exc:
            logger.error(f"Failed to retrieve user info from Google: {exc}")
            raise ApplicationError(
                f"Failed to retrieve user info from Google: {exc}"
            ) from exc

    def refresh_access_token(self, refresh_token: str) -> GoogleAccessToken:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token from previous authentication

        Returns:
            GoogleAccessToken: New token set
        """
        if not refresh_token:
            raise ApplicationError("Refresh token is required")

        data = {
            "client_id": self._credential.client_id,
            "client_secret": self._credential.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(
                self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data, timeout=30
            )
            response.raise_for_status()

            token_data = response.json()

            if "access_token" not in token_data:
                raise ApplicationError("Invalid refresh token response")

            logger.info("Successfully refreshed access token")
            return GoogleAccessToken(
                id_token=token_data.get("id_token", ""),
                access_token=token_data["access_token"],
                refresh_token=refresh_token,  # Keep original refresh token
            )

        except requests.RequestException as exc:
            logger.error(f"Failed to refresh access token: {exc}")
            raise ApplicationError(f"Failed to refresh access token: {exc}") from exc
