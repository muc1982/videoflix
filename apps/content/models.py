"""
Models for the content app.

This module defines the Video model and related choices for the
Videoflix streaming platform.
"""
from django.db import models


class Category(models.TextChoices):
    """Available video categories/genres."""

    ACTION = 'Action', 'Action'
    COMEDY = 'Comedy', 'Comedy'
    DRAMA = 'Drama', 'Drama'
    DOCUMENTARY = 'Documentary', 'Documentary'
    HORROR = 'Horror', 'Horror'
    ROMANCE = 'Romance', 'Romance'
    SCIFI = 'Sci-Fi', 'Sci-Fi'
    THRILLER = 'Thriller', 'Thriller'


class Video(models.Model):
    """
    Video model for storing video metadata and file references.

    Attributes:
        title: The title of the video.
        description: A description of the video content.
        category: The genre/category of the video.
        video_file: The original uploaded video file.
        thumbnail: Optional thumbnail image for the video.
        created_at: Timestamp when the video was created.
        hls_ready: Whether HLS conversion is complete.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.DRAMA
    )
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    hls_ready = models.BooleanField(default=False)

    class Meta:
        """Meta options for Video model."""
        ordering = ['-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        """Return string representation of the video."""
        return self.title

    def get_hls_base_path(self):
        """
        Get the base path for HLS files.

        Returns:
            str: The relative path to the HLS directory for this video.
        """
        return f'hls/{self.id}'

    def get_hls_manifest_path(self, resolution):
        """
        Get the path to the HLS manifest for a specific resolution.

        Args:
            resolution: The video resolution (e.g., '480p', '720p', '1080p').

        Returns:
            str: The relative path to the HLS manifest file.
        """
        return f'{self.get_hls_base_path()}/{resolution}/index.m3u8'

    def get_thumbnail_url(self):
        """
        Get the URL for the video thumbnail.

        Returns:
            str: The URL to the thumbnail, or None if not available.
        """
        if self.thumbnail:
            return self.thumbnail.url
        return None
