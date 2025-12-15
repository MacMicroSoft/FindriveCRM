#!/bin/bash
# Script to sync findrive_crm/.env to root .env for docker-compose

set -e

ENV_SOURCE="findrive_crm/.env"
ENV_TARGET=".env"

if [ ! -f "$ENV_SOURCE" ]; then
    echo "ERROR: $ENV_SOURCE not found!"
    echo "Please create the .env file in findrive_crm directory first."
    exit 1
fi

echo "Syncing $ENV_SOURCE to $ENV_TARGET..."

# Copy the file
cp "$ENV_SOURCE" "$ENV_TARGET"

echo "Done! Both files are now in sync."
echo ""
echo "Source: $ENV_SOURCE"
echo "Target: $ENV_TARGET"
echo ""
echo "Note: When you update findrive_crm/.env, run this script again to sync."

