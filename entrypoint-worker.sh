#!/bin/sh
set -e

echo "=== Videoflix Worker Startup ==="

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/media/videos
mkdir -p /app/media/hls
mkdir -p /app/media/thumbnails

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! python -c "import redis; r = redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null; do
    echo "Redis not ready, waiting..."
    sleep 2
done
echo "Redis is ready!"

echo "=== Starting RQ Worker ==="
exec python manage.py rqworker default
