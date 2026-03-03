"""
Views for the content app.

This module contains API views for video listing and HLS streaming.
"""
import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    """
    API view for listing all available videos.

    Returns video metadata grouped by category for the dashboard.
    """

    def get(self, request):
        """
        Handle GET request for video list.

        Args:
            request: The HTTP request.

        Returns:
            Response: List of video metadata (200) or error (500).
        """
        try:
            videos = Video.objects.filter(hls_ready=True)
            serializer = VideoSerializer(
                videos,
                many=True,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HLSManifestView(APIView):
    """
    API view for serving HLS manifest files.

    Returns the .m3u8 playlist file for a specific video and resolution.
    """

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
            video = Video.objects.get(id=movie_id, hls_ready=True)
        except Video.DoesNotExist:
            raise Http404("Video or manifest not found.")

        if resolution not in settings.VIDEO_RESOLUTIONS:
            raise Http404("Video or manifest not found.")

        manifest_path = (
            Path(settings.MEDIA_ROOT) /
            'hls' /
            str(movie_id) /
            resolution /
            'index.m3u8'
        )

        if not manifest_path.exists():
            raise Http404("Video or manifest not found.")

        return FileResponse(
            open(manifest_path, 'rb'),
            content_type='application/vnd.apple.mpegurl'
        )


class HLSSegmentView(APIView):
    """
    API view for serving HLS video segments.

    Returns individual .ts segment files for video playback.
    """

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
            video = Video.objects.get(id=movie_id, hls_ready=True)
        except Video.DoesNotExist:
            raise Http404("Video or segment not found.")

        if resolution not in settings.VIDEO_RESOLUTIONS:
            raise Http404("Video or segment not found.")

        segment_path = (
            Path(settings.MEDIA_ROOT) /
            'hls' /
            str(movie_id) /
            resolution /
            segment
        )

        if not segment_path.exists():
            raise Http404("Video or segment not found.")

        return FileResponse(
            open(segment_path, 'rb'),
            content_type='video/MP2T'
        )
