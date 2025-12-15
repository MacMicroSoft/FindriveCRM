# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for static files and media
RUN mkdir -p /app/staticfiles /app/media

# Collect static files (will be run again in entrypoint, but this helps with caching)
# RUN python manage.py collectstatic --noinput || true

# Create entrypoint script
RUN chmod +x /app/docker-entrypoint.sh || true

# Expose port
EXPOSE 8000

# Run entrypoint script
CMD ["/app/docker-entrypoint.sh"]

