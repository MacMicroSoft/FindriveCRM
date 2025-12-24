.PHONY: help backup-db restore-db setup-server build up down restart logs shell migrate createsuperuser collectstatic

# Default target
help:
	@echo "Available commands:"
	@echo "  make backup-db          - Export PostgreSQL database to JSON dump"
	@echo "  make restore-db         - Restore PostgreSQL database from JSON dump"
	@echo "  make setup-server       - Setup Linux server (install Docker & Docker Compose)"
	@echo "  make build              - Build Docker images"
	@echo "  make up                 - Start all containers"
	@echo "  make down               - Stop all containers"
	@echo "  make restart            - Restart all containers"
	@echo "  make logs               - View logs from all containers"
	@echo "  make shell              - Open Django shell"
	@echo "  make migrate            - Run database migrations"
	@echo "  make createsuperuser    - Create Django superuser"
	@echo "  make collectstatic      - Collect static files"
	@echo "  make deploy             - Full deployment (build, migrate, collectstatic, up)"

# Database backup to JSON
backup-db:
	@echo "Creating database backup..."
	@mkdir -p backups
	@echo "Exporting to JSON..."
	@docker-compose exec -T web python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > backups/db_dump_$$(date +%Y%m%d_%H%M%S).json || \
		docker-compose exec -T web python manage.py dumpdata --indent 2 > backups/db_dump_$$(date +%Y%m%d_%H%M%S).json
	@echo "JSON backup created in backups/"
	@echo "Backup completed!"

# Restore database from JSON
restore-db:
	@echo "Available backups:"
	@ls -lh backups/*.json 2>/dev/null || echo "No JSON backups found"
	@read -p "Enter backup filename (from backups/): " filename; \
	docker-compose exec -T web python manage.py loaddata backups/$$filename
	@echo "Database restored!"

# Setup Linux server (install Docker & Docker Compose)
setup-server:
	@echo "Setting up Linux server..."
	@echo "Updating system packages..."
	@sudo apt-get update
	@echo "Installing prerequisites..."
	@sudo apt-get install -y \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg \
		lsb-release
	@echo "Adding Docker's official GPG key..."
	@curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
	@echo "Setting up Docker repository..."
	@echo "deb [arch=$$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	@echo "Installing Docker..."
	@sudo apt-get update
	@sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	@echo "Adding current user to docker group..."
	@sudo usermod -aG docker $$USER
	@echo "Starting Docker service..."
	@sudo systemctl start docker
	@sudo systemctl enable docker
	@echo "Installing Docker Compose standalone (if not already installed)..."
	@sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$$(uname -s)-$$(uname -m)" -o /usr/local/bin/docker-compose
	@sudo chmod +x /usr/local/bin/docker-compose
	@echo "Verifying installations..."
	@docker --version
	@docker-compose --version
	@echo ""
	@echo "Setup completed! Please log out and log back in for group changes to take effect."
	@echo "Or run: newgrp docker"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start all containers
up:
	@echo "Starting containers..."
	docker-compose up -d
	@echo "Containers started!"
	@echo "View logs with: make logs"

# Stop all containers
down:
	@echo "Stopping containers..."
	docker-compose down

# Restart all containers
restart:
	@echo "Restarting containers..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Django shell
shell:
	docker-compose exec web python manage.py shell

# Run migrations
migrate:
	@echo "Running migrations..."
	docker-compose exec web python manage.py migrate
	@echo "Migrations completed!"

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Collect static files
collectstatic:
	@echo "Collecting static files..."
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "Static files collected!"

# Full deployment
deploy: build migrate collectstatic up
	@echo "Deployment completed!"
	@echo "Creating superuser..."
	@docker-compose exec web python manage.py createsuperuser || echo "Superuser may already exist"

