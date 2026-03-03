"""
Signals for the content app.

This module contains Django signals for automatic video processing.
"""
import logging

import django_rq
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import convert_video_to_hls, delete_hls_files

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Video post_save.

    Queues HLS conversion task when a new video is uploaded.

    Args:
        sender: The model class (Video).
        instance: The saved Video instance.
        created: Boolean indicating if this is a new instance.
        **kwargs: Additional keyword arguments.
    """
    if created and instance.video_file:
        queue = django_rq.get_queue('default')
        queue.enqueue(convert_video_to_hls, instance.id)
        logger.info(f"Queued HLS conversion for video {instance.id}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal handler for Video post_delete.

    Cleans up HLS files when a video is deleted.

    Args:
        sender: The model class (Video).
        instance: The deleted Video instance.
        **kwargs: Additional keyword arguments.
    """
    if instance.video_file:
        try:
            instance.video_file.delete(save=False)
        except Exception as e:
            logger.error(f"Error deleting video file: {e}")

    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except Exception as e:
            logger.error(f"Error deleting thumbnail: {e}")

    queue = django_rq.get_queue('default')
    queue.enqueue(delete_hls_files, instance.id)
    logger.info(f"Queued HLS cleanup for video {instance.id}")
