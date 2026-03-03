"""
Background tasks for video processing.

This module contains RQ tasks for converting videos to HLS format
using FFmpeg.
"""
import logging
import os
import subprocess
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

RESOLUTION_CONFIG = {
    '480p': {'width': 854, 'height': 480, 'bitrate': '1000k'},
    '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
    '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
}


def convert_video_to_hls(video_id):
    """
    Convert a video to HLS format in multiple resolutions.

    This task runs in the background using Django RQ. It converts
    the original video file to HLS segments for streaming.

    Args:
        video_id: The ID of the Video model instance to convert.
    """
    from apps.content.models import Video

    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        logger.error(f"Video with id {video_id} not found")
        return

    input_path = video.video_file.path
    base_output_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(video.id)

    for resolution, config in RESOLUTION_CONFIG.items():
        convert_to_resolution(input_path, base_output_dir, resolution, config)

    generate_thumbnail(video, input_path)

    video.hls_ready = True
    video.save()
    logger.info(f"Video {video_id} conversion completed")


def convert_to_resolution(input_path, base_output_dir, resolution, config):
    """
    Convert video to a specific resolution using FFmpeg.

    Args:
        input_path: Path to the source video file.
        base_output_dir: Base directory for HLS output.
        resolution: Resolution string (e.g., '720p').
        config: Dictionary with width, height, and bitrate settings.
    """
    output_dir = base_output_dir / resolution
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / 'index.m3u8'
    segment_path = output_dir / '%03d.ts'

    cmd = [
        settings.FFMPEG_PATH,
        '-i', str(input_path),
        '-vf', f"scale={config['width']}:{config['height']}",
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-b:v', config['bitrate'],
        '-c:a', 'aac',
        '-b:a', '128k',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_segment_filename', str(segment_path),
        '-f', 'hls',
        str(output_path),
        '-y'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Converted to {resolution}: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error for {resolution}: {e.stderr}")
        raise


def generate_thumbnail(video, input_path):
    """
    Generate a thumbnail image from the video.

    Extracts a frame from the video at the 5-second mark.

    Args:
        video: The Video model instance.
        input_path: Path to the source video file.
    """
    if video.thumbnail:
        return

    thumbnail_dir = Path(settings.MEDIA_ROOT) / 'thumbnails'
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    thumbnail_path = thumbnail_dir / f'{video.id}.jpg'

    cmd = [
        settings.FFMPEG_PATH,
        '-i', str(input_path),
        '-ss', '00:00:05',
        '-vframes', '1',
        '-vf', 'scale=640:360',
        str(thumbnail_path),
        '-y'
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        video.thumbnail = f'thumbnails/{video.id}.jpg'
        video.save()
        logger.info(f"Generated thumbnail for video {video.id}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Thumbnail generation failed: {e.stderr}")


def delete_hls_files(video_id):
    """
    Delete HLS files for a video.

    Called when a video is deleted to clean up associated files.

    Args:
        video_id: The ID of the deleted video.
    """
    import shutil

    hls_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(video_id)

    if hls_dir.exists():
        shutil.rmtree(hls_dir)
        logger.info(f"Deleted HLS files for video {video_id}")
