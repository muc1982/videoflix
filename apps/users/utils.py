"""
Utility functions for the users app.

This module contains helper functions for email sending and token generation.
"""
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_activation_token(user):
    """
    Generate activation token and uid for a user.

    Args:
        user: The user instance to generate token for.

    Returns:
        tuple: (uidb64, token) for the activation link.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def send_activation_email(user, uidb64, token):
    """
    Send activation email to the user.

    Args:
        user: The user instance.
        uidb64: Base64 encoded user ID.
        token: Activation token.
    """
    activation_link = (
        f"{settings.FRONTEND_URL}/activate/{uidb64}/{token}/"
    )

    html_message = render_to_string('emails/confirm_email.html', {
        'user': user,
        'activation_link': activation_link,
    })

    send_mail(
        subject='Activate your Videoflix account',
        message=f'Click here to activate: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, uidb64, token):
    """
    Send password reset email to the user.

    Args:
        user: The user instance.
        uidb64: Base64 encoded user ID.
        token: Password reset token.
    """
    reset_link = (
        f"{settings.FRONTEND_URL}/password-reset/{uidb64}/{token}/"
    )

    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_link': reset_link,
    })

    send_mail(
        subject='Reset your Videoflix password',
        message=f'Click here to reset your password: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def set_jwt_cookies(response, access_token, refresh_token):
    """
    Set JWT tokens as HttpOnly cookies on the response.

    Args:
        response: The HTTP response object.
        access_token: The JWT access token.
        refresh_token: The JWT refresh token.

    Returns:
        Response: The response with cookies set.
    """
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=str(access_token),
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    response.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=str(refresh_token),
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    return response


def delete_jwt_cookies(response):
    """
    Delete JWT cookies from the response.

    Args:
        response: The HTTP response object.

    Returns:
        Response: The response with cookies deleted.
    """
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    response.delete_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
    )
    return response
