"""
URL routing for the content app.

This module defines all URL patterns for video endpoints.
"""
from django.urls import path

from .legal_views import ImprintView, PrivacyPolicyView
from .views import HLSManifestView, HLSSegmentView, VideoListView

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
