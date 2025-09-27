.PHONY: build up down logs test shell clean

# Default target
help:
	@echo "Available commands:"
	@echo "  build   - Build the Docker images"
	@echo "  up      - Start the services"
	@echo "  down    - Stop the services"
	@echo "  logs    - View logs"
	@echo "  test    - Run tests"
	@echo "  shell   - Get shell access to the API container"
	@echo "  clean   - Remove all containers and volumes"

# Build the Docker images
build:
	docker-compose build

# Start the services
up:
	docker-compose up -d

# Stop the services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run tests
test:
	docker-compose run --rm api pytest tests/

# Get shell access to the API container
shell:
	docker-compose run --rm api bash

# Remove all containers and volumes
clean:
	docker-compose down -v