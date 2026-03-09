#!/bin/sh
set -e

echo "=== Videoflix Backend Startup ==="

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/media/videos
mkdir -p /app/media/hls
mkdir -p /app/media/thumbnails
mkdir -p /app/staticfiles

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations users content --noinput || true
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Starting Django server ==="
exec python manage.py runserver 0.0.0.0:8000
