"""
Views for the content app.

This module contains API views for video listing and HLS streaming.
"""

import logging
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Video
from .serializers import VideoSerializer

logger = logging.getLogger(__name__)


class VideoListView(APIView):
    """
    API view for listing all available videos.

    Returns video metadata grouped by category for the dashboard.

    Status Codes:
        200: Liste erfolgreich zuruckgegeben.
        401: Nicht authentifiziert.
        500: Interner Serverfehler.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for video list.

        Args:
            request: The HTTP request.

        Returns:
            Response: List of video metadata (200) or error (401/500).
        """
        try:
            # Get query parameter to show all videos (for debugging)
            show_all = request.query_params.get("all", "").lower() == "true"

            if show_all:
                videos = Video.objects.all().order_by("-created_at")
            else:
                videos = Video.objects.filter(hls_ready=True).order_by("-created_at")

            serializer = VideoSerializer(
                videos, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching video list: {e}")
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HLSManifestView(APIView):
    """
    API view for serving HLS manifest files.

    Returns the .m3u8 playlist file for a specific video and resolution.

    Status Codes:
        200: Manifest erfolgreich geliefert.
        401: Nicht authentifiziert.
        404: Video oder Manifest nicht gefunden.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """
        Handle GET request for HLS manifest.

        Args:
            request: The HTTP request.
            movie_id: The ID of the video.
            resolution: The requested resolution (480p, 720p, 1080p).

        Returns:
            FileResponse: The HLS manifest file (200) or error (404).
        """
        try:
            Video.objects.get(id=movie_id, hls_ready=True)
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video or manifest not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if resolution not in settings.VIDEO_RESOLUTIONS:
            return Response(
                {"detail": "Video or manifest not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        manifest_path = (
            Path(settings.MEDIA_ROOT)
            / "hls"
            / str(movie_id)
            / resolution
            / "index.m3u8"
        )

        if not manifest_path.exists():
            return Response(
                {"detail": "Video or manifest not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            open(manifest_path, "rb"), content_type="application/vnd.apple.mpegurl"
        )


class HLSSegmentView(APIView):
    """
    API view for serving HLS video segments.

    Returns individual .ts segment files for video playback.

    Status Codes:
        200: Segment erfolgreich geliefert.
        401: Nicht authentifiziert.
        404: Video oder Segment nicht gefunden.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """
        Handle GET request for HLS segment.

        Args:
            request: The HTTP request.
            movie_id: The ID of the video.
            resolution: The requested resolution.
            segment: The segment filename (e.g., '000.ts').

        Returns:
            FileResponse: The video segment file (200) or error (404).
        """
        try:
            Video.objects.get(id=movie_id, hls_ready=True)
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video or segment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if resolution not in settings.VIDEO_RESOLUTIONS:
            return Response(
                {"detail": "Video or segment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        segment_path = (
            Path(settings.MEDIA_ROOT) / "hls" / str(movie_id) / resolution / segment
        )

        if not segment_path.exists():
            return Response(
                {"detail": "Video or segment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(open(segment_path, "rb"), content_type="video/MP2T")


class PrivacyPolicyView(APIView):
    """
    API view for privacy policy information.

    Returns the privacy policy content as JSON.

    Status Codes:
        200: Datenschutzerklarung erfolgreich geliefert.
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
        return Response(
            {
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
                    "contact": "privacy@videoflix.com",
                },
            }
        )


class ImprintView(APIView):
    """
    API view for imprint/legal notice information.

    Returns the imprint content as JSON.

    Status Codes:
        200: Impressum erfolgreich geliefert.
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
        return Response(
            {
                "title": "Imprint",
                "content": {
                    "company_name": "Videoflix GmbH",
                    "address": {
                        "street": "Musterstraße 123",
                        "city": "12345 Berlin",
                        "country": "Germany",
                    },
                    "contact": {
                        "email": "info@videoflix.com",
                        "phone": "+49 123 456789",
                    },
                    "registration": {
                        "court": "Amtsgericht Berlin",
                        "number": "HRB 123456",
                    },
                    "vat_id": "DE123456789",
                    "responsible_person": {
                        "name": "Max Mustermann",
                        "role": "Managing Director",
                    },
                    "disclaimer": (
                        "Despite careful content control, we assume no liability "
                        "for the content of external links. The operators of the "
                        "linked pages are solely responsible for their content."
                    ),
                },
            }
        )
