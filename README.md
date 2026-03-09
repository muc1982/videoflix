"# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

## Features

- **User Authentication**: Registration, login, logout with JWT tokens stored in HttpOnly cookies
- **Email Verification**: Account activation via email confirmation
- **Password Reset**: Secure password reset functionality via email
- **Video Streaming**: HLS video streaming with multiple resolutions (480p, 720p, 1080p, 1440p, 4K)
- **Background Tasks**: Video conversion using Django RQ and FFmpeg
- **Caching**: Redis-based caching for improved performance
- **Production Ready**: Gunicorn WSGI server, Whitenoise for static files

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Django RQ
- **Video Processing**: FFmpeg
- **WSGI Server**: Gunicorn
- **Static Files**: Whitenoise
- **Containerization**: Docker & Docker Compose

## Project Structure

```
videoflix/
├── apps/
│   ├── users/                  # User authentication and account management
│   │   ├── api/                # DRF API layer
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py  # User serializers
│   │   │   ├── views.py        # Auth endpoints
│   │   │   └── urls.py         # URL routing
│   │   ├── models.py           # Custom user model
│   │   ├── authentication.py   # Cookie JWT auth
│   │   └── utils.py            # Helper functions
│   └── content/                # Video content management
│       ├── api/                # DRF API layer
│       │   ├── __init__.py
│       │   ├── serializers.py  # Video serializers
│       │   ├── views.py        # Video streaming endpoints
│       │   └── urls.py         # URL routing
│       ├── models.py           # Video model
│       ├── tasks.py            # FFmpeg background tasks
│       └── signals.py          # Auto video conversion
├── core/                       # Project configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL config
│   ├── wsgi.py                 # WSGI application
│   └── asgi.py                 # ASGI application
├── templates/
│   └── emails/                 # Email templates
├── static/                     # Static assets
├── media/                      # Uploaded files
├── logs/                       # Application logs
├── docker-compose.yml          # Development configuration
├── docker-compose.prod.yml     # Production configuration
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Getting Started

### Prerequisites

- Docker Desktop installed
- Git

### Installation (Development)

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd videoflix
   ```

2. Copy environment file:

   ```bash
   cp .env.example .env
   ```

3. Start the services:

   ```bash
   docker-compose up --build
   ```

4. Create a superuser (in another terminal):

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - RQ Dashboard: http://localhost:8000/django-rq/
   - **Mailhog UI**: http://localhost:8025/ (view sent emails)

### Email Testing with Mailhog

In development mode, emails are sent to Mailhog (a local SMTP testing server). To view sent emails:

1. Open http://localhost:8025/ in your browser
2. All emails (registration confirmation, password reset) will appear here
3. Emails include embedded logos using Content-ID (CID) attachments

**Note**: The `.env` file must have the correct Mailhog settings:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mailhog
EMAIL_PORT=1025
EMAIL_USE_TLS=False
```

### Installation (Production)

1. Configure the `.env` file with production values:

   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. Start with production configuration:

   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. Create a superuser:
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

## API Endpoints

### Authentication

| Endpoint                                  | Method | Description            | Status Codes  |
| ----------------------------------------- | ------ | ---------------------- | ------------- |
| `/api/register/`                          | POST   | Register new user      | 201, 400      |
| `/api/activate/<uidb64>/<token>/`         | GET    | Activate account       | 200, 400      |
| `/api/login/`                             | POST   | User login             | 200, 400      |
| `/api/logout/`                            | POST   | User logout            | 200, 400      |
| `/api/token/refresh/`                     | POST   | Refresh access token   | 200, 400, 401 |
| `/api/password_reset/`                    | POST   | Request password reset | 200           |
| `/api/password_confirm/<uidb64>/<token>/` | POST   | Confirm password reset | 200, 400      |

### Video Content

| Endpoint                                  | Method | Description     | Status Codes  |
| ----------------------------------------- | ------ | --------------- | ------------- |
| `/api/video/`                             | GET    | List all videos | 200, 401, 500 |
| `/api/video/<id>/<resolution>/index.m3u8` | GET    | HLS manifest    | 200, 401, 404 |
| `/api/video/<id>/<resolution>/<segment>`  | GET    | HLS segment     | 200, 401, 404 |

### Legal Pages

| Endpoint        | Method | Description          | Status Codes |
| --------------- | ------ | -------------------- | ------------ |
| `/api/privacy/` | GET    | Privacy policy       | 200          |
| `/api/imprint/` | GET    | Imprint/Legal notice | 200          |

## Environment Variables

| Variable               | Description                        | Default                 |
| ---------------------- | ---------------------------------- | ----------------------- |
| `DEBUG`                | Debug mode                         | `False`                 |
| `SECRET_KEY`           | Django secret key                  | -                       |
| `DATABASE_URL`         | PostgreSQL connection URL          | -                       |
| `REDIS_URL`            | Redis connection URL               | -                       |
| `EMAIL_BACKEND`        | Email backend class                | SMTP backend            |
| `EMAIL_HOST`           | SMTP server host                   | `mailhog` (dev)         |
| `EMAIL_PORT`           | SMTP server port                   | `1025` (dev)            |
| `FRONTEND_URL`         | Frontend URL for email links       | `http://localhost:5500` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins               | -                       |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins (Django 4.x+) | -                       |
| `ALLOWED_HOSTS`        | Allowed host headers               | `localhost,127.0.0.1`   |

## Video Upload

Videos can be uploaded via the Django Admin interface:

1. Login to `/admin/`
2. Go to Content > Videos
3. Add a new video with title, description, category, and video file
4. The video will automatically be converted to HLS format in the background

### Supported Resolutions

Videos are automatically converted to the following resolutions (if source quality allows):

| Resolution | Width  | Bitrate  |
| ---------- | ------ | -------- |
| 480p       | 854px  | 1.5 Mbps |
| 720p       | 1280px | 4 Mbps   |
| 1080p      | 1920px | 8 Mbps   |
| 1440p      | 2560px | 12 Mbps  |
| 4K         | 3840px | 20 Mbps  |

### Video Troubleshooting

If videos are not showing up in the frontend:

1. **Check if the RQ Worker is running**:

   ```bash
   docker-compose logs worker
   ```

2. **Check if FFmpeg is available**:

   ```bash
   docker-compose exec web which ffmpeg
   ```

3. **Check video conversion status in Admin**:
   - Videos with `hls_ready=True` are visible to users
   - Use the \"Mark as ready\" action in Admin to manually enable videos (for testing)
   - Use the \"Trigger HLS conversion\" action to retry conversion

4. **View all videos (including non-converted)**:
   - Add `?all=true` to the video API endpoint: `/api/video/?all=true`

5. **Check RQ Dashboard**:
   - Visit http://localhost:8000/django-rq/ to see queued/failed jobs

## Testing

Run the API endpoint tests:

```bash
python test_endpoints.py
```

This script tests all authentication and video endpoints with expected status codes.

## Commit History Guidelines

Each feature should be committed separately:

1. `feat: initial project setup with Docker configuration`
2. `feat: add custom user model and authentication`
3. `feat: add email verification and password reset`
4. `feat: add video model and HLS streaming`
5. `feat: add FFmpeg background tasks for video conversion`
6. `feat: add 4K and 1440p video support`
7. `fix: add CSRF_TRUSTED_ORIGINS for Django 4.x compatibility`
8. `docs: add README and API documentation`

## License

This project is for educational purposes only.
"
