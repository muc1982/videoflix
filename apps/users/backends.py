"""
Custom authentication backend for email-based login.

This module provides an authentication backend that allows users to log in
using their email address instead of a username.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that uses email for authentication.

    This backend authenticates users using their email address
    instead of the default username field.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user based on email and password.

        Args:
            request: The HTTP request.
            email: The user's email address.
            password: The user's password.
            **kwargs: Additional keyword arguments.

        Returns:
            User: The authenticated user, or None if authentication fails.
        """
        if email is None:
            email = kwargs.get("username")

        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run password hasher to prevent timing attacks
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Get a user by their primary key.

        Args:
            user_id: The user's primary key.

        Returns:
            User: The user instance, or None if not found.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
