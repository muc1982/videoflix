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

# Create superuser automatically if environment variables are set
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Checking for superuser..."
    python manage.py shell -c "
from apps.users.models import CustomUser
if not CustomUser.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    CustomUser.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
" 2>/dev/null || echo "Superuser creation skipped (may already exist)"
else
    echo "No DJANGO_SUPERUSER_EMAIL/PASSWORD set - skipping automatic superuser creation"
    echo "To create manually: docker-compose exec web python manage.py createsuperuser"
fi

echo "=== Starting Django server ==="
exec python manage.py runserver 0.0.0.0:8000
