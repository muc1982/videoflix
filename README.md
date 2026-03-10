# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

## Features

- **User Authentication**: Registration, login, logout with JWT tokens stored in HttpOnly cookies
- **Email Verification**: Account activation via email confirmation
- **Password Reset**: Secure password reset functionality via email
- **Video Streaming**: HLS video streaming with multiple resolutions (480p, 720p, 1080p)
- **Automatic Thumbnail Generation**: Thumbnails are auto-generated from videos during upload
- **Background Tasks**: Video conversion using Django RQ and FFmpeg
- **Caching**: Redis-based caching for improved performance

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Django RQ
- **Video Processing**: FFmpeg
- **Containerization**: Docker & Docker Compose

## Quick Start (2 Steps)

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

**That's it!** A default admin user is automatically created:

- **Email**: `admin@videoflix.com`
- **Password**: `admin123`

### Access the Application

| Service          | URL                              |
| ---------------- | -------------------------------- |
| API              | http://localhost:8000/api/       |
| Admin            | http://localhost:8000/admin/     |
| Mailhog (Emails) | http://localhost:8025/           |
| RQ Dashboard     | http://localhost:8000/django-rq/ |

### Optional: Custom Superuser

Set environment variables in `.env` before startup:

```bash
DJANGO_SUPERUSER_EMAIL=your-email@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

Or create manually after startup:

```bash
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting

### Windows Users: Line Endings

If the project fails on Mac/Linux with "bad interpreter" errors:

```bash
git config --global core.autocrlf input
```

The `.gitattributes` file handles this automatically.

### Mac M1/M2 Users (Mailhog Issue)

The `platform: linux/amd64` flag ensures Mailhog works on Apple Silicon:

```bash
docker-compose down -v
docker-compose up --build
```

### Video List Empty After Login

If `/api/video/` returns an empty array:

1. **Check Admin Panel**: Go to Content > Videos - do videos exist?
2. **Check HLS status**: Videos need `hls_ready=True` to appear
3. **Check Worker**: `docker-compose logs worker`
4. **Manual fix**: Admin > Videos > Select > "Mark as ready"

### Worker Not Processing Videos

```bash
docker-compose logs worker
docker-compose restart worker
```

## API Endpoints

### Authentication

| Endpoint                       | Method | Description            |
| ------------------------------ | ------ | ---------------------- |
| `/api/register/`               | POST   | Register new user      |
| `/api/activate/<uid>/<token>/` | GET    | Activate account       |
| `/api/login/`                  | POST   | User login             |
| `/api/logout/`                 | POST   | User logout            |
| `/api/token/refresh/`          | POST   | Refresh JWT token      |
| `/api/password_reset/`         | POST   | Request password reset |

### Video Content

| Endpoint                                  | Method | Description             |
| ----------------------------------------- | ------ | ----------------------- |
| `/api/video/`                             | GET    | List all ready videos   |
| `/api/video/?all=true`                    | GET    | List ALL videos (debug) |
| `/api/video/<id>/<resolution>/index.m3u8` | GET    | HLS manifest            |

## Video Upload & Processing

### Upload via Admin

1. Go to http://localhost:8000/admin/
2. Login with admin credentials
3. Navigate to **Content > Videos**
4. Click **Add Video**
5. Upload a video file (MP4 recommended)
6. Save

The video will automatically be:

- Converted to HLS format (480p, 720p, 1080p)
- Have a thumbnail generated

### Supported Resolutions

| Resolution | Width  | Bitrate  |
| ---------- | ------ | -------- |
| 480p       | 854px  | 1.5 Mbps |
| 720p       | 1280px | 4 Mbps   |
| 1080p      | 1920px | 8 Mbps   |

### Check Conversion Status

- Visit http://localhost:8000/django-rq/ to see queued jobs
- Videos with `hls_ready=True` appear in the API
- Thumbnails are auto-generated

## Environment Variables

| Variable                    | Description              | Default                 |
| --------------------------- | ------------------------ | ----------------------- |
| `DJANGO_SUPERUSER_EMAIL`    | Auto-created admin email | `admin@videoflix.com`   |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin pass  | `admin123`              |
| `FRONTEND_URL`              | Frontend URL for emails  | `http://localhost:5500` |
| `CORS_ALLOWED_ORIGINS`      | Allowed CORS origins     | (see .env.example)      |

## License

This project is for educational purposes only.
