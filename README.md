# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

## Features

- **User Authentication**: Registration, login, logout with JWT tokens stored in HttpOnly cookies
- **Email Verification**: Account activation via email confirmation
- **Password Reset**: Secure password reset functionality via email
- **Video Streaming**: HLS video streaming with multiple resolutions (480p, 720p, 1080p)
- **Background Tasks**: Video conversion using Django RQ and FFmpeg
- **Caching**: Redis-based caching for improved performance

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Django RQ
- **Video Processing**: FFmpeg
- **Containerization**: Docker & Docker Compose

## Project Structure

```
videoflix/
├── apps/
│   ├── users/          # User authentication and account management
│   │   ├── models.py   # Custom user model
│   │   ├── views.py    # Auth endpoints
│   │   ├── serializers.py
│   │   └── urls.py
│   └── content/        # Video content management
│       ├── models.py   # Video model
│       ├── views.py    # Video streaming endpoints
│       ├── tasks.py    # FFmpeg background tasks
│       └── signals.py  # Auto video conversion
├── templates/
│   └── emails/         # Email templates
├── static/             # Static assets
├── media/              # Uploaded files
├── videoflix/          # Project configuration
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Getting Started

### Prerequisites

- Docker Desktop installed
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd videoflix
   ```

2. Start the services:
   ```bash
   docker-compose up --build
   ```

3. Create a superuser (in another terminal):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - RQ Dashboard: http://localhost:8000/django-rq/

## API Endpoints

### Authentication

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/register/` | POST | Register new user | No |
| `/api/activate/<uidb64>/<token>/` | GET | Activate account | No |
| `/api/login/` | POST | User login | No |
| `/api/logout/` | POST | User logout | Refresh Token |
| `/api/token/refresh/` | POST | Refresh access token | Refresh Token |
| `/api/password_reset/` | POST | Request password reset | No |
| `/api/password_confirm/<uidb64>/<token>/` | POST | Confirm password reset | No |

### Video Content

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/video/` | GET | List all videos | JWT |
| `/api/video/<id>/<resolution>/index.m3u8` | GET | HLS manifest | JWT |
| `/api/video/<id>/<resolution>/<segment>` | GET | HLS segment | JWT |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | - |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `REDIS_URL` | Redis connection URL | - |
| `EMAIL_BACKEND` | Email backend class | Console backend |
| `FRONTEND_URL` | Frontend URL for email links | `http://localhost:5500` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | - |

## Video Upload

Videos can be uploaded via the Django Admin interface:

1. Login to `/admin/`
2. Go to Content > Videos
3. Add a new video with title, description, category, and video file
4. The video will automatically be converted to HLS format in the background

## Commit History Guidelines

Each feature should be committed separately:

1. `feat: initial project setup with Docker configuration`
2. `feat: add custom user model and authentication`
3. `feat: add email verification and password reset`
4. `feat: add video model and HLS streaming`
5. `feat: add FFmpeg background tasks for video conversion`
6. `docs: add README and API documentation`

## License

This project is for educational purposes only.
