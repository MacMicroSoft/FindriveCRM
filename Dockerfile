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

# Copy entrypoint script first and set permissions
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Copy project
COPY . /app/

# Create directories for static files and media
RUN mkdir -p /app/staticfiles /app/media

# Ensure entrypoint script has execute permissions (in case it was overwritten by COPY)
RUN chmod +x /app/docker-entrypoint.sh || true

# Expose port
EXPOSE 8000

# Run entrypoint script
CMD ["/app/docker-entrypoint.sh"]

