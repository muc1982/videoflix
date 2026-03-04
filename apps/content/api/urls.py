"""
URL routing for the content app API.

This module defines all URL patterns for video endpoints.
"""
from django.urls import path

from .views import (
    HLSManifestView,
    HLSSegmentView,
    ImprintView,
    PrivacyPolicyView,
    VideoListView,
)

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),
    path(
        'video/<int:movie_id>/<str:resolution>/index.m3u8',
        HLSManifestView.as_view(),
        name='hls_manifest'
    ),
    path(
        'video/<int:movie_id>/<str:resolution>/<str:segment>',
        HLSSegmentView.as_view(),
        name='hls_segment'
    ),
    # Legal pages
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('imprint/', ImprintView.as_view(), name='imprint'),
]
