"""
Custom JWT authentication using HttpOnly cookies.

This module provides cookie-based JWT authentication for the Videoflix API.
"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads tokens from HttpOnly cookies.

    This provides enhanced security by preventing JavaScript access to tokens.
    """

    def authenticate(self, request):
        """
        Authenticate the request using JWT token from cookies.

        Args:
            request: The HTTP request object.

        Returns:
            tuple: (user, validated_token) if authentication succeeds.
            None: If no token is present in cookies.
        """
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
