"""
Views for legal information pages.

This module provides API endpoints for legal pages like
privacy policy and imprint.
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class PrivacyPolicyView(APIView):
    """
    API view for privacy policy information.

    Returns the privacy policy content as JSON.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return privacy policy content.

        Args:
            request: The HTTP request.

        Returns:
            Response: Privacy policy data.
        """
        return Response({
            "title": "Privacy Policy",
            "last_updated": "2024-01-01",
            "content": {
                "introduction": (
                    "Welcome to Videoflix. We take your privacy seriously. "
                    "This policy describes how we collect, use, and protect "
                    "your personal information."
                ),
                "data_collection": (
                    "We collect information you provide directly, such as "
                    "your email address when you register. We also collect "
                    "usage data to improve our service."
                ),
                "data_usage": (
                    "Your data is used to provide and improve our streaming "
                    "service, send important notifications, and ensure "
                    "account security."
                ),
                "data_protection": (
                    "We implement industry-standard security measures to "
                    "protect your personal information from unauthorized "
                    "access or disclosure."
                ),
                "cookies": (
                    "We use essential cookies for authentication purposes. "
                    "These cookies are necessary for the service to function "
                    "properly."
                ),
                "user_rights": (
                    "You have the right to access, correct, or delete your "
                    "personal data. Contact us to exercise these rights."
                ),
                "contact": "privacy@videoflix.com"
            }
        })


class ImprintView(APIView):
    """
    API view for imprint/legal notice information.

    Returns the imprint content as JSON.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return imprint content.

        Args:
            request: The HTTP request.

        Returns:
            Response: Imprint data.
        """
        return Response({
            "title": "Imprint",
            "content": {
                "company_name": "Videoflix GmbH",
                "address": {
                    "street": "Musterstraße 123",
                    "city": "12345 Berlin",
                    "country": "Germany"
                },
                "contact": {
                    "email": "info@videoflix.com",
                    "phone": "+49 123 456789"
                },
                "registration": {
                    "court": "Amtsgericht Berlin",
                    "number": "HRB 123456"
                },
                "vat_id": "DE123456789",
                "responsible_person": {
                    "name": "Max Mustermann",
                    "role": "Managing Director"
                },
                "disclaimer": (
                    "Despite careful content control, we assume no liability "
                    "for the content of external links. The operators of the "
                    "linked pages are solely responsible for their content."
                )
            }
        })
