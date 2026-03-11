# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

> ⚠️ **IMPORTANT: Always use `127.0.0.1` in your browser, NOT `localhost`!**
>
> The frontend is configured to use `127.0.0.1:8000` for API calls. Using `localhost` will cause authentication errors.
>
> ✅ Correct: `http://127.0.0.1:5500/`
> ❌ Wrong: `http://localhost:5500/`

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

**Important:** Edit `.env` and set `FRONTEND_URL` to match your frontend port.

**You MUST use `127.0.0.1` (not `localhost`)** because the frontend uses `127.0.0.1` for API calls:

```bash
# Default port 5500 (VS Code Live Server)
FRONTEND_URL=http://127.0.0.1:5500
```

Then open the frontend in your browser using `127.0.0.1`:

- ✅ `http://127.0.0.1:5500/`
- ❌ `http://localhost:5500/` (will cause authentication issues)

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

| Service      | URL                              |
| ------------ | -------------------------------- |
| API          | http://127.0.0.1:8000/api/       |
| Admin        | http://127.0.0.1:8000/admin/     |
| RQ Dashboard | http://127.0.0.1:8000/django-rq/ |

**Important:** Always use `127.0.0.1` instead of `localhost` in the browser!

### Email Configuration (Required!)

Configure your own SMTP provider in `.env` to send real emails:

```bash
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password-or-app-password
DEFAULT_FROM_EMAIL=Videoflix <your-email@example.com>
```

**Common SMTP Settings:**

| Provider | EMAIL_HOST          | EMAIL_PORT | EMAIL_USE_TLS |
| -------- | ------------------- | ---------- | ------------- |
| Gmail    | smtp.gmail.com      | 587        | True          |
| GMX      | mail.gmx.net        | 587        | True          |
| Web.de   | smtp.web.de         | 587        | True          |
| Outlook  | smtp.office365.com  | 587        | True          |
| Yahoo    | smtp.mail.yahoo.com | 587        | True          |

**Note:** Some providers (Gmail, Yahoo) require an App Password instead of your regular password.

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

## Supported Frontend Ports (CORS)

The backend is configured to accept requests from the following frontend origins by default:

| Framework / Tool    | Ports                  |
| ------------------- | ---------------------- |
| VS Code Live Server | 5500, 5501, 5502, 5503 |
| React               | 3000                   |
| Angular             | 4200                   |
| Vue                 | 8080                   |

Both `localhost` and `127.0.0.1` are supported for all ports.

**Custom CORS Origins:** You can set custom origins in `.env`:

```bash
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500,http://127.0.0.1:5501,http://127.0.0.1:6000
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500,http://127.0.0.1:5501,http://127.0.0.1:6000
```

## Troubleshooting

### 401 Unauthorized / Access Token Error

If you get "Authentication credentials were not provided" or 401 errors:

**The frontend uses `127.0.0.1:8000` for API calls.** You MUST access the frontend via `127.0.0.1`, not `localhost`:

| Browser URL              | Works? |
| ------------------------ | ------ |
| `http://127.0.0.1:5500/` | ✅ Yes |
| `http://localhost:5500/` | ❌ No  |

**Why?** `localhost` and `127.0.0.1` are treated as different domains by browsers. Cookies set for one won't be sent to the other.

### Before Testing: Clear Browser Data

Before testing the application, clear your browser's cookies and cache to avoid authentication issues:

**Chrome:**

1. Press `F12` to open Developer Tools
2. Go to **Application** → **Cookies**
3. Right-click on `127.0.0.1` and select **Clear**
4. Refresh the page

**Or use Incognito/Private Mode** for a fresh session.

### Email Links Point to Wrong Port

If activation or password reset links point to the wrong port:

1. Edit `.env` file
2. Set `FRONTEND_URL` to match your frontend port:
   ```bash
   FRONTEND_URL=http://127.0.0.1:5500
   ```
3. Restart Docker:
   ```bash
   docker-compose down
   docker-compose up
   ```

### Windows Users: Line Endings

If the project fails on Mac/Linux with "bad interpreter" errors:

```bash
git config --global core.autocrlf input
```

The `.gitattributes` file handles this automatically.

### Video List Empty After Login

If `/api/video/` returns an empty array:

1. **Check Admin Panel**: Go to Content > Videos - do videos exist?
2. **Check HLS status**: Videos need `hls_ready=True` to appear
3. **Manual fix**: Admin > Videos > Select > "Mark as ready"

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

| Endpoint                                  | Method | Description           | Status Codes  |
| ----------------------------------------- | ------ | --------------------- | ------------- |
| `/api/video/`                             | GET    | List all ready videos | 200, 401      |
| `/api/video/<id>/<resolution>/index.m3u8` | GET    | HLS manifest          | 200, 401, 404 |
| `/api/video/<id>/<resolution>/<segment>`  | GET    | HLS video segment     | 200, 401, 404 |

### Legal

| Endpoint        | Method | Description    | Status Codes |
| --------------- | ------ | -------------- | ------------ |
| `/api/privacy/` | GET    | Privacy policy | 200          |
| `/api/imprint/` | GET    | Imprint        | 200          |

## Video Upload & Processing

### Upload via Admin

1. Go to http://127.0.0.1:8000/admin/
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

- Visit http://127.0.0.1:8000/django-rq/ to see queued jobs
- Videos with `hls_ready=True` appear in the API
- Thumbnails are auto-generated

## Environment Variables

| Variable                    | Description                  | Default                 |
| --------------------------- | ---------------------------- | ----------------------- |
| `DEBUG`                     | Enable debug mode            | `False`                 |
| `SECRET_KEY`                | Django secret key            | (required)              |
| `DATABASE_URL`              | PostgreSQL connection string | (required)              |
| `REDIS_URL`                 | Redis connection string      | (required)              |
| `FRONTEND_URL`              | Frontend URL for email links | `http://127.0.0.1:5500` |
| `BACKEND_URL`               | Backend URL                  | `http://127.0.0.1:8000` |
| `DJANGO_SUPERUSER_EMAIL`    | Auto-created admin email     | `admin@videoflix.com`   |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin pass      | `admin123`              |
| `CORS_ALLOWED_ORIGINS`      | Comma-separated CORS origins | (defaults in settings)  |
| `CSRF_TRUSTED_ORIGINS`      | Comma-separated CSRF origins | (defaults in settings)  |
| `EMAIL_HOST`                | SMTP server host             | (required)              |
| `EMAIL_PORT`                | SMTP server port             | `587`                   |
| `EMAIL_USE_TLS`             | Use TLS for email            | `True`                  |
| `EMAIL_HOST_USER`           | SMTP username                | (required)              |
| `EMAIL_HOST_PASSWORD`       | SMTP password                | (required)              |

## Project Structure

```
videoflix/
├── apps/
│   ├── users/                    # User authentication
│   │   ├── api/                  # REST API endpoints
│   │   │   ├── serializers.py    # Request/response serializers
│   │   │   ├── urls.py           # URL routing
│   │   │   └── views.py          # API views
│   │   ├── authentication.py     # Cookie JWT authentication
│   │   ├── backends.py           # Email authentication backend
│   │   ├── models.py             # Custom user model
│   │   └── utils.py              # Email helpers
│   └── content/                  # Video content
│       ├── api/                  # Video streaming endpoints
│       │   ├── serializers.py    # Video serializers
│       │   ├── urls.py           # URL routing
│       │   └── views.py          # HLS streaming views
│       ├── admin.py              # Admin configuration
│       ├── models.py             # Video model
│       ├── signals.py            # Auto video processing
│       └── tasks.py              # FFmpeg conversion & thumbnails
├── core/                         # Django configuration
│   ├── exception_handler.py      # Custom 401 response handler
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI application
├── templates/emails/             # Email templates
├── static/                       # Static assets
├── media/                        # Uploaded videos
├── docker-compose.yml            # Docker configuration
├── .Dockerfile                   # Container definition
├── entrypoint.sh                 # Web server startup script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitattributes                # Git line ending config
└── README.md                     # This file
```

## License

This project is for educational purposes only.
