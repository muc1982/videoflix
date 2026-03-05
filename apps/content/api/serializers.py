"""
Serializers for the content app.

This module contains serializers for video data representation.
"""

from rest_framework import serializers

from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video model.

    Provides video metadata for the frontend dashboard.
    """

    thumbnail_url = serializers.SerializerMethodField()
    video_file_url = serializers.SerializerMethodField()

    class Meta:
        """Meta options for VideoSerializer."""

        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
            "hls_ready",
            "video_file_url",
        ]

    def get_thumbnail_url(self, obj):
        """
        Get the full URL for the video thumbnail.

        Args:
            obj: The Video instance.

        Returns:
            str: The absolute URL to the thumbnail, or None.
        """
        request = self.context.get("request")
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_video_file_url(self, obj):
        """
        Get the full URL for the original video file.

        Args:
            obj: The Video instance.

        Returns:
            str: The absolute URL to the video file, or None.
        """
        request = self.context.get("request")
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return None
