"""
Admin configuration for the content app.

This module registers the Video model in the Django admin.
"""

import django_rq
from django.contrib import admin, messages
from django.utils.html import mark_safe

from .models import Video
from .tasks import convert_video_to_hls, generate_thumbnail


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""

    list_display = ["title", "category", "has_thumbnail", "hls_ready", "created_at"]
    list_filter = ["category", "hls_ready", "created_at"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "hls_ready", "thumbnail_preview"]
    actions = ["trigger_hls_conversion", "mark_as_ready", "generate_thumbnails"]

    fieldsets = (
        (None, {"fields": ("title", "description", "category")}),
        ("Media", {"fields": ("video_file", "thumbnail", "thumbnail_preview")}),
        ("Status", {"fields": ("created_at", "hls_ready"), "classes": ("collapse",)}),
    )

    @admin.display(boolean=True, description="Thumbnail")
    def has_thumbnail(self, obj):
        """Check if video has a thumbnail."""
        return bool(obj.thumbnail)

    @admin.display(description="Thumbnail Preview")
    def thumbnail_preview(self, obj):
        """Show thumbnail preview in admin."""
        if obj.thumbnail:
            return mark_safe(
                f'<img src="{obj.thumbnail.url}" style="max-height: 100px;" />'
            )
        return "No thumbnail"

    @admin.action(description="Trigger HLS conversion for selected videos")
    def trigger_hls_conversion(self, request, queryset):
        """Queue HLS conversion for selected videos."""
        queue = django_rq.get_queue("default")
        count = 0
        for video in queryset:
            if video.video_file:
                queue.enqueue(convert_video_to_hls, video.id)
                count += 1
        self.message_user(
            request, f"Queued HLS conversion for {count} video(s).", messages.SUCCESS
        )

    @admin.action(description="Mark selected videos as HLS ready")
    def mark_as_ready(self, request, queryset):
        """Mark selected videos as HLS ready (for testing)."""
        count = queryset.update(hls_ready=True)
        self.message_user(
            request, f"Marked {count} video(s) as HLS ready.", messages.SUCCESS
        )

    @admin.action(description="Generate thumbnails for selected videos")
    def generate_thumbnails(self, request, queryset):
        """Generate thumbnails for selected videos."""
        from .tasks import generate_thumbnail as gen_thumb

        count = 0
        for video in queryset:
            if video.video_file and not video.thumbnail:
                try:
                    gen_thumb(video, video.video_file.path)
                    count += 1
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error generating thumbnail for {video.title}: {e}",
                        messages.ERROR,
                    )
        self.message_user(
            request, f"Generated thumbnails for {count} video(s).", messages.SUCCESS
        )
