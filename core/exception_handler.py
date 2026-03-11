"""
Custom exception handler for DRF.

Returns 401 Unauthorized for authentication failures instead of 403 Forbidden.
"""

from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns 401 for authentication failures.

    DRF by default returns 403 Forbidden when authentication fails.
    This handler converts it to 401 Unauthorized which is more appropriate.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Convert 403 to 401 for authentication/permission failures
        if response.status_code == status.HTTP_403_FORBIDDEN:
            # Check if this is an authentication issue
            request = context.get("request")
            if request and not request.user.is_authenticated:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                response.data = {
                    "detail": "Authentication credentials were not provided or are invalid."
                }

    return response
