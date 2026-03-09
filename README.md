# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

## Features

- **User Authentication**: Registration, login, logout with JWT tokens stored in HttpOnly cookies
- **Email Verification**: Account activation via email confirmation
- **Password Reset**: Secure password reset functionality via email
- **Video Streaming**: HLS video streaming with multiple resolutions (480p, 720p, 1080p, 1440p, 4K)
- **Automatic Thumbnail Generation**: Thumbnails are auto-generated from videos during upload
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

You can customize these credentials by editing the `.env` file before starting.

### Access the Application

| Service          | URL                              |
| ---------------- | -------------------------------- |
| API              | http://localhost:8000/api/       |
| Admin            | http://localhost:8000/admin/     |
| Mailhog (Emails) | http://localhost:8025/           |
| RQ Dashboard     | http://localhost:8000/django-rq/ |

### Optional: Custom Superuser

To create a superuser with custom credentials, either:

**Option A**: Set environment variables in `.env` before startup:

```bash
DJANGO_SUPERUSER_EMAIL=your-email@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

**Option B**: Create manually after startup:

```bash
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting

### Windows Users: Line Endings

If you develop on Windows and the project fails on Mac/Linux with errors like "bad interpreter", ensure Git uses correct line endings:

```bash
# Before cloning (one-time global setting)
git config --global core.autocrlf input

# Or after cloning, fix line endings
git add --renormalize .
git commit -m "Fix line endings"
```

The `.gitattributes` file in this project should handle this automatically.

### Mac M1/M2 Users (Mailhog Issue)

The `platform: linux/amd64` flag in docker-compose.yml ensures Mailhog works on Apple Silicon. If issues persist:

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

### Video List Empty After Login

If the video list API returns an empty array:

1. **Check if videos exist**: Go to Admin Panel > Content > Videos
2. **Check HLS ready status**: Videos must have `hls_ready=True` to appear
3. **Trigger conversion manually**:
   - In Admin, select videos and use "Trigger HLS conversion" action
   - Or use "Mark as ready" for testing
4. **Check worker is running**: `docker-compose logs worker`

### Worker Not Processing Videos

```bash
# Check worker status
docker-compose logs worker

# Restart worker
docker-compose restart worker
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
│       ├── signals.py          # Auto video processing
│       └── tasks.py            # FFmpeg conversion & thumbnails
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

| Endpoint                                  | Method | Description                           | Status Codes  |
| ----------------------------------------- | ------ | ------------------------------------- | ------------- |
| `/api/video/`                             | GET    | List all videos                       | 200, 401, 500 |
| `/api/video/?all=true`                    | GET    | List ALL videos (including not ready) | 200, 401, 500 |
| `/api/video/<id>/<resolution>/index.m3u8` | GET    | HLS manifest                          | 200, 404      |
| `/api/video/<id>/<resolution>/<segment>`  | GET    | HLS segment                           | 200, 404      |

### Legal Pages

| Endpoint        | Method | Description    |
| --------------- | ------ | -------------- |
| `/api/privacy/` | GET    | Privacy policy |
| `/api/imprint/` | GET    | Legal notice   |

## Environment Variables

| Variable                    | Description              | Default                 |
| --------------------------- | ------------------------ | ----------------------- |
| `DEBUG`                     | Debug mode               | `True`                  |
| `SECRET_KEY`                | Django secret key        | auto-generated          |
| `DATABASE_URL`              | PostgreSQL URL           | (set in docker-compose) |
| `REDIS_URL`                 | Redis URL                | (set in docker-compose) |
| `DJANGO_SUPERUSER_EMAIL`    | Auto-created admin email | `admin@videoflix.com`   |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin pass  | `admin123`              |
| `EMAIL_HOST`                | SMTP host                | `mailhog`               |
| `EMAIL_PORT`                | SMTP port                | `1025`                  |
| `FRONTEND_URL`              | Frontend URL for emails  | `http://localhost:5500` |
| `CORS_ALLOWED_ORIGINS`      | Allowed CORS origins     | (see .env.example)      |
| `CSRF_TRUSTED_ORIGINS`      | CSRF trusted origins     | (see .env.example)      |

## Video Upload & Streaming

### Upload via Admin

1. Go to http://localhost:8000/admin/
2. Login with admin credentials
3. Navigate to **Content > Videos**
4. Click **Add Video**
5. Fill in title, description, category
6. Upload a video file (MP4 recommended)
7. Save

The video will automatically be:

- Converted to HLS format in multiple resolutions
- Have a thumbnail generated from the first seconds

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
- Thumbnails are auto-generated; no manual upload needed

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
