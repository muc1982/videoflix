# Videoflix Backend - Commit Guide

This guide helps you commit the project step by step for your exam.

## Recommended Commit Order

### Commit 1: Initial Project Setup
```bash
git init
git add docker-compose.yml Dockerfile requirements.txt manage.py .gitignore .env.example README.md
git add videoflix/__init__.py videoflix/settings.py videoflix/urls.py videoflix/wsgi.py videoflix/asgi.py
git add static/logo.svg
git commit -m "feat: initial Django project setup with Docker configuration"
```

### Commit 2: Custom User Model and Authentication
```bash
git add apps/__init__.py
git add apps/users/__init__.py apps/users/apps.py apps/users/models.py apps/users/admin.py
git add apps/users/authentication.py
git commit -m "feat: add custom user model with email-based authentication"
```

### Commit 3: User Registration and Activation
```bash
git add apps/users/serializers.py apps/users/utils.py
git add apps/users/views.py apps/users/urls.py
git add templates/emails/confirm_email.html
git commit -m "feat: add user registration with email verification"
```

### Commit 4: Login, Logout and Password Reset
```bash
git add templates/emails/password_reset.html
git commit -m "feat: add login, logout and password reset functionality"
```

### Commit 5: Video Content Model
```bash
git add apps/content/__init__.py apps/content/apps.py apps/content/models.py apps/content/admin.py
git add apps/content/serializers.py
git commit -m "feat: add video model with category support"
```

### Commit 6: HLS Video Streaming
```bash
git add apps/content/views.py apps/content/urls.py
git commit -m "feat: add HLS video streaming endpoints"
```

### Commit 7: Background Video Processing
```bash
git add apps/content/tasks.py apps/content/signals.py
git commit -m "feat: add FFmpeg background tasks for video conversion"
```

### Commit 8: Media Directory Structure
```bash
git add media/videos/.gitkeep media/thumbnails/.gitkeep media/hls/.gitkeep
git commit -m "chore: add media directory structure"
```

### Final Commit: Documentation
```bash
git add COMMIT_GUIDE.md
git commit -m "docs: add commit guide and finalize documentation"
```

## Quick Start After Cloning

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. In a new terminal, run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

## Testing the API

### Register a new user
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!", "confirmed_password": "TestPass123!"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}' \
  -c cookies.txt
```

### Get videos (authenticated)
```bash
curl -X GET http://localhost:8000/api/video/ \
  -b cookies.txt
```
