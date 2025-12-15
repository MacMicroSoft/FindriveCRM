#!/bin/bash
# Script to initialize Let's Encrypt certificates

set -e

DOMAIN_NAME=${DOMAIN_NAME:-localhost}
CERTBOT_EMAIL=${CERTBOT_EMAIL:-admin@example.com}

echo "=========================================="
echo "Initializing Let's Encrypt SSL Certificate"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN_NAME"
echo "Email: $CERTBOT_EMAIL"
echo ""

# Check if domain is localhost (won't work with Let's Encrypt)
if [ "$DOMAIN_NAME" = "localhost" ]; then
    echo "WARNING: localhost cannot get Let's Encrypt certificate!"
    echo "Please set DOMAIN_NAME environment variable to your actual domain."
    echo ""
    echo "Example:"
    echo "  export DOMAIN_NAME=yourdomain.com"
    echo "  export CERTBOT_EMAIL=your@email.com"
    echo "  ./init-letsencrypt.sh"
    exit 1
fi

echo "Step 1: Starting nginx with HTTP only..."
# Temporarily use HTTP-only config
docker-compose up -d nginx

echo ""
echo "Step 2: Waiting for nginx to be ready..."
sleep 5

echo ""
echo "Step 3: Requesting SSL certificate from Let's Encrypt..."
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email "$CERTBOT_EMAIL" --agree-tos --no-eff-email -d "$DOMAIN_NAME"

echo ""
echo "Step 3.5: Updating nginx config with domain name..."
# Update nginx config with actual domain
sed -i "s/yourdomain.com/$DOMAIN_NAME/g" nginx/conf.d/findrive.conf

echo ""
echo "Step 4: Restarting nginx with SSL configuration..."
docker-compose restart nginx

echo ""
echo "=========================================="
echo "SSL Certificate setup complete!"
echo "=========================================="
echo ""
echo "Your site should now be available at: https://$DOMAIN_NAME"
echo ""
echo "To renew certificates (runs automatically), use:"
echo "  docker-compose run --rm certbot renew"
echo ""

