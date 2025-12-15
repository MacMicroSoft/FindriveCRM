#!/bin/bash
# Script to reset database and fix authentication issues

set -e

echo "=========================================="
echo "Resetting PostgreSQL Database"
echo "=========================================="
echo ""
echo "WARNING: This will delete all database data!"
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

echo ""
echo "Step 1: Stopping containers..."
docker-compose down

echo ""
echo "Step 2: Removing database volume..."
docker volume rm findrivecrm_postgres_data 2>/dev/null || docker volume rm findrive_project_postgres_data 2>/dev/null || echo "Volume not found or already removed"

echo ""
echo "Step 3: Verifying .env file exists..."
if [ ! -f findrive_crm/.env ]; then
    echo "ERROR: findrive_crm/.env file not found!"
    echo "Please create it with the following variables:"
    echo "  DB_NAME=findrive_db"
    echo "  DB_USER=findrive_user"
    echo "  DB_PASSWORD=your-secure-password"
    echo "  DB_HOST=db"
    echo "  DB_PORT=5432"
    exit 1
fi

echo ""
echo "Step 4: Checking .env file format..."
if grep -E "^[^#].*#.*" findrive_crm/.env > /dev/null 2>&1; then
    echo "WARNING: Found inline comments in .env file!"
    echo "Removing inline comments..."
    ./fix-env.sh || echo "fix-env.sh not found, please fix manually"
fi

echo ""
echo "Step 5: Starting containers..."
docker-compose up -d --build

echo ""
echo "Step 6: Waiting for database to be ready..."
sleep 5

echo ""
echo "Step 7: Checking container status..."
docker-compose ps

echo ""
echo "=========================================="
echo "Database reset complete!"
echo "=========================================="
echo ""
echo "To view logs, run:"
echo "  docker-compose logs -f web"
echo ""

