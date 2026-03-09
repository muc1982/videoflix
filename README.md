# Videoflix Backend

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

## Quick Start (3 Steps)

### Prerequisites

- Docker Desktop installed and running
- Git

### Step 1: Clone and Setup

```bash
git clone <repository-url>
cd videoflix
cp .env.example .env
```

### Step 2: Start Services

```bash
docker-compose up --build
```

Wait until you see:

```
videoflix_web | === Starting Django server ===
```

### Step 3: Create Admin User

Open a new terminal:

```bash
docker-compose exec web python manage.py createsuperuser
```

### Done! Access the application:

| Service          | URL                              |
| ---------------- | -------------------------------- |
| API              | http://localhost:8000/api/       |
| Admin            | http://localhost:8000/admin/     |
| Mailhog (Emails) | http://localhost:8025/           |
| RQ Dashboard     | http://localhost:8000/django-rq/ |

## Troubleshooting

### Mac M1/M2 Users (Mailhog Issue)

If Mailhog fails to start on Apple Silicon, the `platform: linux/amd64` flag in docker-compose.yml should handle this. If issues persist:

```bash
# Remove old containers and rebuild
docker-compose down -v
docker-compose up --build
```

### Database Connection Issues

```bash
# Check if all services are running
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs db
```

### Permission Errors

```bash
# Reset volumes and rebuild
docker-compose down -v
docker-compose up --build
```

## Project Structure

```
videoflix/
├── apps/
│   ├── users/                  # User authentication
│   │   ├── api/                # REST API endpoints
│   │   ├── models.py           # Custom user model
│   │   └── utils.py            # Email helpers
│   └── content/                # Video content
│       ├── api/                # Video streaming endpoints
│       ├── models.py           # Video model
│       └── tasks.py            # FFmpeg conversion
├── core/                       # Django settings
├── templates/emails/           # Email templates
├── static/                     # Static assets (Logo)
├── media/                      # Uploaded videos
├── logs/                       # Application logs
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container definition
├── entrypoint.sh              # Web server startup script
├── entrypoint-worker.sh       # Worker startup script
└── requirements.txt            # Python dependencies
```

## API Endpoints

### Authentication

| Endpoint                               | Method | Description            | Status Codes  |
| -------------------------------------- | ------ | ---------------------- | ------------- |
| `/api/register/`                       | POST   | Register new user      | 201, 400      |
| `/api/activate/<uid>/<token>/`         | GET    | Activate account       | 200, 400      |
| `/api/login/`                          | POST   | User login             | 200, 400      |
| `/api/logout/`                         | POST   | User logout            | 200           |
| `/api/token/refresh/`                  | POST   | Refresh JWT token      | 200, 400, 401 |
| `/api/password_reset/`                 | POST   | Request password reset | 200           |
| `/api/password_confirm/<uid>/<token>/` | POST   | Confirm new password   | 200, 400      |

### Video Content

| Endpoint                                  | Method | Description     | Status Codes  |
| ----------------------------------------- | ------ | --------------- | ------------- |
| `/api/video/`                             | GET    | List all videos | 200, 401, 500 |
| `/api/video/<id>/<resolution>/index.m3u8` | GET    | HLS manifest    | 200, 404      |
| `/api/video/<id>/<resolution>/<segment>`  | GET    | HLS segment     | 200, 404      |

### Legal Pages

| Endpoint        | Method | Description    |
| --------------- | ------ | -------------- |
| `/api/privacy/` | GET    | Privacy policy |
| `/api/imprint/` | GET    | Legal notice   |

## Environment Variables

| Variable               | Description             | Default                 |
| ---------------------- | ----------------------- | ----------------------- |
| `DEBUG`                | Debug mode              | `True`                  |
| `SECRET_KEY`           | Django secret key       | auto-generated          |
| `DATABASE_URL`         | PostgreSQL URL          | (set in docker-compose) |
| `REDIS_URL`            | Redis URL               | (set in docker-compose) |
| `EMAIL_HOST`           | SMTP host               | `mailhog`               |
| `EMAIL_PORT`           | SMTP port               | `1025`                  |
| `FRONTEND_URL`         | Frontend URL for emails | `http://localhost:5500` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins    | (see .env.example)      |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins    | (see .env.example)      |

## Video Upload & Streaming

### Upload via Admin

1. Go to http://localhost:8000/admin/
2. Navigate to **Content > Videos**
3. Click **Add Video**
4. Fill in title, description, category
5. Upload a video file (MP4 recommended)
6. Save

The video will automatically be converted to HLS format in the background.

### Supported Resolutions

| Resolution | Width  | Bitrate  |
| ---------- | ------ | -------- |
| 480p       | 854px  | 1.5 Mbps |
| 720p       | 1280px | 4 Mbps   |
| 1080p      | 1920px | 8 Mbps   |
| 1440p      | 2560px | 12 Mbps  |
| 4K         | 3840px | 20 Mbps  |

### Check Conversion Status

- Visit http://localhost:8000/django-rq/ to see queued jobs
- Videos with `hls_ready=True` are visible to users
- Use Admin action "Mark as ready" for testing

## Email Testing with Mailhog

All emails (registration, password reset) are caught by Mailhog in development:

1. Open http://localhost:8025/
2. See all sent emails
3. Click activation/reset links directly from Mailhog

## Testing API Endpoints

Run the included test script:

```bash
python test_endpoints.py
```

This tests all authentication and video endpoints.

## License

This project is for educational purposes only.
