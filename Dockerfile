FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create media directories
RUN mkdir -p /app/media/videos /app/media/thumbnails /app/media/hls

# Create logs directory
RUN mkdir -p /app/logs

# Collect static files
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Default command (use gunicorn for production)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "core.wsgi:application"]
