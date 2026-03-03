"""
Serializers for the users app.

This module contains all serializers for user authentication and management.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data representation."""

    class Meta:
        """Meta options for UserSerializer."""
        model = User
        fields = ['id', 'email', 'username']
        read_only_fields = ['id', 'username']


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.

    Validates email, password, and password confirmation.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirmed_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        """
        Validate that the email is not already in use.

        Args:
            value: The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If email is already registered.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your input and try again."
            )
        return value

    def validate(self, attrs):
        """
        Validate that passwords match.

        Args:
            attrs: The validated attributes.

        Returns:
            dict: The validated attributes.

        Raises:
            ValidationError: If passwords don't match.
        """
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({
                "confirmed_password": "Please check your input and try again."
            })
        return attrs

    def create(self, validated_data):
        """
        Create a new user with the validated data.

        Args:
            validated_data: The validated registration data.

        Returns:
            User: The created user instance (inactive until email verified).
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login credentials."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.

    Validates new password and confirmation.
    """

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        """
        Validate that new passwords match.

        Args:
            attrs: The validated attributes.

        Returns:
            dict: The validated attributes.

        Raises:
            ValidationError: If passwords don't match.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        return attrs
