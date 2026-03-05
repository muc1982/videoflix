"""
Views for user authentication and account management.

This module contains all API views for user registration, login, logout,
account activation, and password reset functionality.
"""

from typing import Any, Dict, cast

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..utils import (
    delete_jwt_cookies,
    generate_activation_token,
    send_activation_email,
    send_password_reset_email,
    set_jwt_cookies,
)
from .serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def get_jwt_settings() -> Dict[str, Any]:
    """Get JWT settings from Django settings."""
    return getattr(settings, "SIMPLE_JWT", {})


class RegisterView(APIView):
    """
    API view for user registration.

    Creates a new inactive user and sends an activation email.

    Status Codes:
        201: Benutzer erfolgreich registriert.
        400: Ungultige Eingabedaten.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        Handle user registration request.

        Args:
            request: HTTP request with registration data.

        Returns:
            Response: User data and activation token on success (201).
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uidb64, token = generate_activation_token(user)
            send_activation_email(user, uidb64, token)

            return Response(
                {"user": UserSerializer(user).data, "token": token},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"detail": "Please check your input and try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ActivateAccountView(APIView):
    """
    API view for account activation.

    Activates a user account using the token from the activation email.

    Status Codes:
        200: Konto erfolgreich aktiviert.
        400: Aktivierung fehlgeschlagen.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, uidb64: str, token: str) -> Response:
        """
        Handle account activation request.

        Args:
            request: HTTP request.
            uidb64: Base64 encoded user ID.
            token: Activation token.

        Returns:
            Response: Success message (200) or error (400).
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Activation failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Activation failed."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    """
    API view for user login.

    Authenticates user and sets JWT tokens as HttpOnly cookies.

    Status Codes:
        200: Login erfolgreich.
        400: Ungultige Anmeldedaten.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        Handle user login request.

        Args:
            request: HTTP request with login credentials.

        Returns:
            Response: User data with JWT cookies set on success (200).
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data: Dict[str, Any] = cast(Dict[str, Any], serializer.validated_data)
        email = validated_data.get("email", "")
        password = validated_data.get("password", "")

        user = authenticate(request._request, email=email, password=password)

        if user is None:
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "Please check your input and try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "detail": "Login successful",
                "user": {"id": user.pk, "username": user.email},
            },
            status=status.HTTP_200_OK,
        )

        return set_jwt_cookies(response, access, refresh)


class LogoutView(APIView):
    """
    API view for user logout.

    Blacklists the refresh token and deletes JWT cookies.

    Status Codes:
        200: Logout erfolgreich.
        400: Refresh Token fehlt.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        Handle user logout request.

        Args:
            request: HTTP request.

        Returns:
            Response: Success message (200) or error (400).
        """
        jwt_settings = get_jwt_settings()
        cookie_name = str(jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"))
        refresh_token = request.COOKIES.get(cookie_name)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response = Response(
            {"detail": "Logout successful! All tokens will be deleted."},
            status=status.HTTP_200_OK,
        )

        return delete_jwt_cookies(response)


class TokenRefreshView(APIView):
    """
    API view for refreshing access tokens.

    Issues a new access token using the refresh token from cookies.

    Status Codes:
        200: Token erfolgreich erneuert.
        400: Refresh Token fehlt.
        401: Ungultiger Refresh Token.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        Handle token refresh request.

        Args:
            request: HTTP request.

        Returns:
            Response: New access token (200) or error (400/401).
        """
        jwt_settings = get_jwt_settings()
        cookie_name = str(jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"))
        refresh_token = request.COOKIES.get(cookie_name)

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            response = Response(
                {"detail": "Token refreshed", "access": str(access)},
                status=status.HTTP_200_OK,
            )

            response.set_cookie(
                key=str(jwt_settings.get("AUTH_COOKIE", "access_token")),
                value=str(access),
                httponly=bool(jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True)),
                secure=bool(jwt_settings.get("AUTH_COOKIE_SECURE", False)),
                samesite=str(jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax")),
                path=str(jwt_settings.get("AUTH_COOKIE_PATH", "/")),
            )

            return response

        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class PasswordResetRequestView(APIView):
    """
    API view for password reset request.

    Sends a password reset email to the user.

    Status Codes:
        200: E-Mail gesendet (immer, aus Sicherheitsgrunden).
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        Handle password reset request.

        Args:
            request: HTTP request with email.

        Returns:
            Response: Success message (200). Always returns success for security.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            validated_data: Dict[str, Any] = cast(
                Dict[str, Any], serializer.validated_data
            )
            email = validated_data.get("email", "")
            try:
                user = User.objects.get(email=email)
                uidb64, token = generate_activation_token(user)
                send_password_reset_email(user, uidb64, token)
            except User.DoesNotExist:
                pass

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    API view for password reset confirmation.

    Resets the user's password using the token from the email.

    Status Codes:
        200: Passwort erfolgreich zuruckgesetzt.
        400: Zurucksetzung fehlgeschlagen.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, uidb64: str, token: str) -> Response:
        """
        Handle password reset confirmation.

        Args:
            request: HTTP request with new password.
            uidb64: Base64 encoded user ID.
            token: Password reset token.

        Returns:
            Response: Success message (200) or error (400).
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Password reset failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Password reset failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            validated_data: Dict[str, Any] = cast(
                Dict[str, Any], serializer.validated_data
            )
            new_password = validated_data.get("new_password", "")
            user.set_password(new_password)
            user.save()
            return Response(
                {"detail": "Your Password has been successfully reset."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Password reset failed."},
            status=status.HTTP_400_BAD_REQUEST,
        )
