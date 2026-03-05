"""
Admin configuration for the content app.

This module registers the Video model in the Django admin.
"""

import django_rq
from django.contrib import admin, messages

from .models import Video
from .tasks import convert_video_to_hls


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""

    list_display = ["title", "category", "created_at", "hls_ready"]
    list_filter = ["category", "hls_ready", "created_at"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "hls_ready"]
    actions = ["trigger_hls_conversion", "mark_as_ready"]

    fieldsets = (
        (None, {"fields": ("title", "description", "category")}),
        ("Media", {"fields": ("video_file", "thumbnail")}),
        ("Status", {"fields": ("created_at", "hls_ready"), "classes": ("collapse",)}),
    )

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
