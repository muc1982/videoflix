"""
Utility functions for the users app.

This module contains helper functions for email sending and token generation.
"""

from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_activation_token(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def _attach_inline_logo(msg: EmailMultiAlternatives) -> None:
    logo_path = Path(settings.BASE_DIR) / "static" / "Logo.png"
    if not logo_path.exists():
        return

    with logo_path.open("rb") as f:
        img = MIMEImage(f.read(), _subtype="png")

    # MUST match HTML: cid:videoflix_logo
    img.add_header("Content-ID", "<videoflix_logo>")
    img.add_header("Content-Disposition", "inline", filename="Logo.png")

    # Django runtime supports attaching MIME parts, typing stubs complain -> ignore
    msg.attach(img)  # type: ignore[arg-type]


def _send_transactional_email(
    *, subject: str, to_email: str, html: str, text: str
) -> None:
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    # IMPORTANT: set related BEFORE adding alternatives/attachments
    msg.mixed_subtype = "related"

    # Add HTML alternative
    msg.attach_alternative(html, "text/html")

    # Attach CID image
    _attach_inline_logo(msg)

    msg.send(fail_silently=False)


def send_activation_email(user, uidb64, token):
    activation_link = (
        f"{settings.FRONTEND_URL}/frontend/pages/auth/activate.html"
        f"?uid={uidb64}&token={token}"
    )

    html = render_to_string(
        "emails/confirm_email.html",
        {"user": user, "activation_link": activation_link},
    )
    text = f"Activate your Videoflix account: {activation_link}"

    _send_transactional_email(
        subject="Confirm your email",
        to_email=user.email,
        html=html,
        text=text,
    )


def send_password_reset_email(user, uidb64, token):
    reset_link = (
        f"{settings.FRONTEND_URL}/frontend/pages/auth/confirm_password.html"
        f"?uid={uidb64}&token={token}"
    )

    html = render_to_string(
        "emails/password_reset.html",
        {"user": user, "reset_link": reset_link},
    )
    text = f"Reset your Videoflix password: {reset_link}"

    _send_transactional_email(
        subject="Reset your password",
        to_email=user.email,
        html=html,
        text=text,
    )


def set_jwt_cookies(response, access_token, refresh_token):
    jwt_settings = getattr(settings, "SIMPLE_JWT", {})

    response.set_cookie(
        key=jwt_settings.get("AUTH_COOKIE", "access_token"),
        value=str(access_token),
        httponly=jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
        secure=jwt_settings.get("AUTH_COOKIE_SECURE", False),
        samesite=jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
        path=jwt_settings.get("AUTH_COOKIE_PATH", "/"),
    )
    response.set_cookie(
        key=jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        value=str(refresh_token),
        httponly=jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
        secure=jwt_settings.get("AUTH_COOKIE_SECURE", False),
        samesite=jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
        path=jwt_settings.get("AUTH_COOKIE_PATH", "/"),
    )
    return response


def delete_jwt_cookies(response):
    jwt_settings = getattr(settings, "SIMPLE_JWT", {})

    response.delete_cookie(
        jwt_settings.get("AUTH_COOKIE", "access_token"),
        path=jwt_settings.get("AUTH_COOKIE_PATH", "/"),
    )
    response.delete_cookie(
        jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        path=jwt_settings.get("AUTH_COOKIE_PATH", "/"),
    )
    return response
