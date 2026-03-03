"""
Content app configuration.

This module configures the content application for Django.
"""
from django.apps import AppConfig


class ContentConfig(AppConfig):
    """Configuration class for the content application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content'
    verbose_name = 'Content'

    def ready(self):
        """Import signals when app is ready."""
        import apps.content.signals  # noqa: F401
