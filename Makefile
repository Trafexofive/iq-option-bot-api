.PHONY: help build up down logs test shell clean install dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Start development environment"
	@echo "  build    - Build all Docker images"
	@echo "  up       - Start all services"
	@echo "  down     - Stop all services"
	@echo "  logs     - View logs from all services"
	@echo "  test     - Run all tests"
	@echo "  shell    - Get shell access to trading bot"
	@echo "  clean    - Remove all containers and volumes"

# Install dependencies
install:
	pip install -r requirements.txt

# Start development environment
dev:
	docker-compose -f infra/docker-compose.yml up -d

# Build all Docker images
build:
	docker-compose -f infra/docker-compose.yml build

# Start all services
up:
	docker-compose -f infra/docker-compose.yml up -d

# Stop all services
down:
	docker-compose -f infra/docker-compose.yml down

# View logs from all services
logs:
	docker-compose -f infra/docker-compose.yml logs -f

# Run all tests
test:
	python -m pytest testing/ -v
	docker-compose -f infra/docker-compose.yml run --rm trading-bot pytest tests/

# Get shell access to trading bot
shell:
	docker-compose -f infra/docker-compose.yml exec trading-bot bash

# Remove all containers and volumes
clean:
	docker-compose -f infra/docker-compose.yml down -v
	docker system prune -f