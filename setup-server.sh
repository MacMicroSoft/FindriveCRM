#!/bin/bash
set -e

echo "=========================================="
echo "Linux Server Setup Script"
echo "Installing Docker & Docker Compose"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please do not run as root. The script will use sudo when needed."
   exit 1
fi

# Update system packages
echo ""
echo "Step 1: Updating system packages..."
sudo apt-get update

# Install prerequisites
echo ""
echo "Step 2: Installing prerequisites..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git

# Add Docker's official GPG key
echo ""
echo "Step 3: Adding Docker's official GPG key..."
if [ ! -f /usr/share/keyrings/docker-archive-keyring.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
fi

# Set up Docker repository
echo ""
echo "Step 4: Setting up Docker repository..."
ARCH=$(dpkg --print-architecture)
DISTRO=$(lsb_release -cs)
echo "deb [arch=${ARCH} signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu ${DISTRO} stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo ""
echo "Step 5: Installing Docker..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group
echo ""
echo "Step 6: Adding current user to docker group..."
sudo usermod -aG docker $USER

# Start and enable Docker service
echo ""
echo "Step 7: Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose standalone (backup method)
echo ""
echo "Step 8: Installing Docker Compose standalone..."
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Verify installations
echo ""
echo "Step 9: Verifying installations..."
echo "Docker version:"
docker --version
echo ""
echo "Docker Compose version:"
docker-compose --version || docker compose version

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "IMPORTANT: Please log out and log back in"
echo "for group changes to take effect."
echo ""
echo "Or run: newgrp docker"
echo ""
echo "After that, you can run:"
echo "  make build    - Build Docker images"
echo "  make up       - Start containers"
echo "  make deploy   - Full deployment"
echo "=========================================="

