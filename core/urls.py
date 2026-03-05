"""
URL configuration for Videoflix project.

This module defines the main URL routing for the entire application.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.users.api.urls")),
    path("api/", include("apps.content.api.urls")),
    path("django-rq/", include("django_rq.urls")),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files from STATICFILES_DIRS in development
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
