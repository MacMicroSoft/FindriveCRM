#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
max_attempts=60
attempt=0
while ! nc -z db 5432; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "ERROR: PostgreSQL is not available after $max_attempts attempts"
    exit 1
  fi
  echo "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
if ! python manage.py migrate --noinput; then
    echo "ERROR: Migrations failed!"
    exit 1
fi

echo "Collecting static files..."
if ! python manage.py collectstatic --noinput; then
    echo "WARNING: collectstatic failed, but continuing..."
fi

echo "Starting Gunicorn..."
# Calculate workers: (2 x CPU cores) + 1, but at least 2 and at most 4
WORKERS=${GUNICORN_WORKERS:-3}
TIMEOUT=${GUNICORN_TIMEOUT:-120}

exec gunicorn findrive_crm.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output

