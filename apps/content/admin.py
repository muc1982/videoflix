"""
Admin configuration for the content app.

This module registers the Video model in the Django admin.
"""
from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""

    list_display = [
        'title',
        'category',
        'created_at',
        'hls_ready'
    ]
    list_filter = ['category', 'hls_ready', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'hls_ready']

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('Media', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Status', {
            'fields': ('created_at', 'hls_ready'),
            'classes': ('collapse',)
        }),
    )
