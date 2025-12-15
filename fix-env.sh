#!/bin/bash
# Script to fix .env file by removing inline comments

if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "Fixing .env file (removing inline comments)..."

# Create backup
cp .env .env.backup

# Remove inline comments (everything after # on lines with =)
# But keep lines that start with #
sed -i 's/^\([^#]*=.*\)#.*$/\1/' .env

# Remove trailing whitespace
sed -i 's/[[:space:]]*$//' .env

# Remove empty lines at the end
sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' .env

echo "Done! Backup saved to .env.backup"
echo ""
echo "New .env file:"
echo "---"
cat .env
echo "---"


