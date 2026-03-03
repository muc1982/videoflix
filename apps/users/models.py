"""
Custom User model for Videoflix.

This module defines the custom user model with email-based authentication.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model with email as identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given email and password.

        Args:
            email: The user's email address.
            password: The user's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given email and password.

        Args:
            email: The superuser's email address.
            password: The superuser's password.
            **extra_fields: Additional fields for the user model.

        Returns:
            CustomUser: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model using email as the primary identifier.

    Attributes:
        email: Unique email address for the user.
        username: Optional username field (auto-generated from email).
        is_active: Whether the user account is activated.
    """

    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        """Meta options for CustomUser model."""
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        """Return string representation of the user."""
        return self.email

    def save(self, *args, **kwargs):
        """
        Save the user instance.

        Auto-generates username from email if not provided.
        """
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
