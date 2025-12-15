#!/bin/bash
set -e

echo "=========================================="
echo "Deploying Findrive Project"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Build images
echo ""
echo "Step 1: Building Docker images..."
docker-compose build

# Start database first
echo ""
echo "Step 2: Starting database..."
docker-compose up -d db

# Wait for database to be ready
echo ""
echo "Step 3: Waiting for database to be ready..."
sleep 5
until docker-compose exec -T db pg_isready -U $(grep DB_USER .env | cut -d '=' -f2 | tr -d ' ') > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "Database is ready!"

# Run migrations
echo ""
echo "Step 4: Running migrations..."
docker-compose exec -T web python manage.py migrate --noinput || \
    docker-compose run --rm web python manage.py migrate --noinput

# Collect static files
echo ""
echo "Step 5: Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput || \
    docker-compose run --rm web python manage.py collectstatic --noinput

# Start all containers
echo ""
echo "Step 6: Starting all containers..."
docker-compose up -d

# Wait a moment for services to start
sleep 3

# Check if containers are running
echo ""
echo "Step 7: Checking container status..."
docker-compose ps

echo ""
echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "Your application should be available at:"
echo "  - HTTP:  http://localhost"
echo "  - HTTPS: https://localhost (if configured)"
echo ""
echo "To create a superuser, run:"
echo "  make createsuperuser"
echo ""
echo "To view logs, run:"
echo "  make logs"
echo "=========================================="

