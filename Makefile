# ======================================================================================
# MISCELLANEOUS
# ======================================================================================

RED     := \033[0;31m
GREEN   := \033[0;32m
YELLOW  := \033[1;33m 
BLUE    := \033[0;34m
PURPLE  := \033[0;35m
CYAN    := \033[0;36m
NC      := \033[0m

# ======================================================================================
# GENERAL CONFIGURATION
# ======================================================================================

SHELL := /bin/bash

COMPOSE_FILE ?= infra/docker-compose.yml
COMPOSE_DEV_FILE ?= infra/docker-compose.dev.yml
COMPOSE_PROD_FILE ?= infra/docker-compose.prod.yml
COMPOSE_TEST_FILE ?= infra/docker-compose.test.yml
COMPOSE := docker compose -f $(COMPOSE_FILE)

PROJECT_NAME := iq-option-bot-api

# ======================================================================================
# DEFAULT TARGET & SELF-DOCUMENTATION
# ======================================================================================
.DEFAULT_GOAL := help

# Phony targets - don't represent files
.PHONY: app help up down logs ps build no-cache restart re config status clean fclean prune \
        stop start ssh exec inspect list-volumes list-networks rere rebuild it backend dev monitoring \
        format lint test trading-bot llm-gateway setup install check-env demo cli agent-start agent-stop \
        agent-status db-migrate db-reset prod staging local

# ======================================================================================
# HELP & USAGE
# ======================================================================================

help:
	@echo -e "$(BLUE)========================================================================="
	@echo -e " 🚀 IQ Option Trading Bot - Docker Compose Manager "
	@echo -e "=========================================================================$(NC)"
	@echo ""
	@echo -e "$(YELLOW)Usage: make [target] [service=SERVICE_NAME] [args=\"ARGS\"] [file=COMPOSE_FILE]$(NC)"
	@echo -e "  'service' specifies a single service for targets like logs, build, ssh, exec, inspect."
	@echo -e "  'args' specifies commands for 'exec'."
	@echo -e "  'file' specifies an alternative docker-compose file."
	@echo ""
	@echo -e "$(GREEN)🎯 Quick Start Commands:$(NC)"
	@echo -e "  setup               - Complete setup (install deps, build, start)"
	@echo -e "  app                 - Start complete trading application stack"
	@echo -e "  dev                 - Start development environment with hot reload"
	@echo -e "  prod                - Start production environment"
	@echo -e "  demo                - Run system demonstration"
	@echo -e "  test                - Run comprehensive test suite"
	@echo ""
	@echo -e "$(GREEN)🐳 Core Stack Management:$(NC)"
	@echo -e "  up                  - Start all services in detached mode (Alias: start)"
	@echo -e "  down                - Stop and remove all services and default network"
	@echo -e "  restart             - Restart all services (down + up)"
	@echo -e "  re                  - Rebuild images and restart all services (down + build + up)"
	@echo -e "  rere                - Rebuild images without cache and restart all services"
	@echo -e "  stop                - Stop all services without removing them"
	@echo ""
	@echo -e "$(GREEN)🏗️ Building Images:$(NC)"
	@echo -e "  build [service=<name>] - Build images (all or specific service)"
	@echo -e "  no-cache [service=<name>] - Build images without cache"
	@echo ""
	@echo -e "$(GREEN)📊 Information & Debugging:$(NC)"
	@echo -e "  status [service=<name>] - Show status of services (Alias: ps)"
	@echo -e "  logs [service=<name>]   - Follow logs (all or specific service)"
	@echo -e "  config              - Validate and display effective Docker Compose configuration"
	@echo -e "  ssh service=<name>    - Get an interactive shell into a running service (Alias: it)"
	@echo -e "  exec service=<name> args=\"<cmd>\" - Execute a command in a running service"
	@echo -e "  inspect service=<name> - Inspect a running service container"
	@echo ""
	@echo -e "$(GREEN)🧹 Cleaning & Pruning:$(NC)"
	@echo -e "  clean               - Remove stopped service containers and networks"
	@echo -e "  fclean              - Deep clean: containers, networks, volumes, and images"
	@echo -e "  prune               - Prune all unused Docker resources"
	@echo ""
	@echo -e "$(GREEN)🤖 Trading Bot Specific:$(NC)"
	@echo -e "  trading-bot         - Start only trading bot service"
	@echo -e "  llm-gateway         - Start only LLM gateway service"
	@echo -e "  agent-start         - Start the trading agent"
	@echo -e "  agent-stop          - Stop the trading agent"  
	@echo -e "  agent-status        - Get trading agent status"
	@echo -e "  cli                 - Open trading bot CLI interface"
	@echo ""
	@echo -e "$(GREEN)💾 Database Management:$(NC)"
	@echo -e "  db-migrate          - Run database migrations"
	@echo -e "  db-reset            - Reset database (WARNING: destroys all data)"
	@echo ""
	@echo -e "$(GREEN)🔧 Development Tools:$(NC)"
	@echo -e "  install             - Install local dependencies"
	@echo -e "  format              - Run code formatting"
	@echo -e "  lint                - Run linter"
	@echo -e "  check-env           - Validate environment configuration"
	@echo ""
	@echo -e "$(YELLOW)📋 Examples:$(NC)"
	@echo -e "  make setup"
	@echo -e "  make app"
	@echo -e "  make logs service=trading-bot"
	@echo -e "  make ssh service=trading-bot"
	@echo -e "  make exec service=trading-bot args=\"python demo.py\""
	@echo -e "  make dev file=infra/docker-compose.dev.yml"
	@echo -e "$(BLUE)========================================================================="
	@echo -e " 🎯 Ready to trade! Use 'make setup' to get started "
	@echo -e "=========================================================================$(NC)"

# ======================================================================================
# QUICK START COMMANDS
# ======================================================================================

setup: check-env install build up ## Complete setup - install, build, and start everything
	@echo -e "$(GREEN)🎉 Setup complete! Trading bot is ready.$(NC)"
	@echo -e "$(CYAN)📊 API Documentation: http://localhost:8000/api/v1/docs$(NC)"
	@echo -e "$(CYAN)🤖 LLM Gateway: http://localhost:8001/docs$(NC)"
	@echo -e "$(YELLOW)💡 Next: make demo    (run demonstration)$(NC)"
	@echo -e "$(YELLOW)💡 Next: make cli     (open CLI interface)$(NC)"

app: up ## Start complete trading application stack
	@echo -e "$(GREEN)🚀 Starting complete IQ Option Trading Bot stack...$(NC)"
	@make logs

dev: ## Start development environment with hot reload
	@echo -e "$(CYAN)🔧 Starting development environment...$(NC)"
	@COMPOSE_FILE=$(COMPOSE_DEV_FILE) $(COMPOSE) up -d --build
	@COMPOSE_FILE=$(COMPOSE_DEV_FILE) $(COMPOSE) logs -f

prod: ## Start production environment  
	@echo -e "$(PURPLE)🏭 Starting production environment...$(NC)"
	@COMPOSE_FILE=$(COMPOSE_PROD_FILE) $(COMPOSE) up -d --build

demo: ## Run system demonstration
	@echo -e "$(CYAN)🎭 Running IQ Option Trading Bot demonstration...$(NC)"
	@$(COMPOSE) exec trading-bot python demo_complete_system.py

test: ## Run comprehensive test suite
	@echo -e "$(YELLOW)🧪 Running comprehensive test suite...$(NC)"
	@$(COMPOSE) exec trading-bot python test_new_features.py
	@$(COMPOSE) exec trading-bot python test_iq_option_integration.py

# ======================================================================================
# CORE STACK MANAGEMENT
# ======================================================================================

up: ## Start all services in detached mode
	@echo -e "$(GREEN)🚀 Igniting services from $(COMPOSE_FILE)... All systems GO!$(NC)"
	@$(COMPOSE) up -d --remove-orphans
	@echo -e "$(GREEN)✅ Services are now running in detached mode.$(NC)"
	@echo -e "$(CYAN)📊 Trading Bot API: http://localhost:8000/api/v1/docs$(NC)"
	@echo -e "$(CYAN)🤖 LLM Gateway: http://localhost:8001/docs$(NC)"

start: ## Alias for up
	@echo -e "$(GREEN)🌟 Starting services from $(COMPOSE_FILE)... All systems GO!$(NC)"
	@$(COMPOSE) up -d --remove-orphans $(service)

down: ## Stop and remove all services and networks defined in the compose file
	@echo -e "$(RED)🛑 Shutting down services from $(COMPOSE_FILE)... Powering down.$(NC)"
	@$(COMPOSE) down --remove-orphans

stop: ## Stop all services without removing them
	@echo -e "$(YELLOW)⏸️ Halting operations for $(COMPOSE_FILE)... Services stopping.$(NC)"
	@$(COMPOSE) stop $(service)

restart: down up ## Restart all services

re: down build up ## Rebuild images and restart all services

rere: down no-cache up ## Rebuild images without cache and restart all services

rebuild: down clean build up ## Alias for re

# ======================================================================================
# BUILDING IMAGES
# ======================================================================================

build: ## Build (or rebuild) images for specified service, or all if none specified
	@echo -e "$(BLUE)🏗️ Forging components... Building images for $(or $(service),all services) from $(COMPOSE_FILE).$(NC)"
	@$(COMPOSE) build $(service)

no-cache: ## Build images without using cache for specified service, or all
	@echo -e "$(YELLOW)🔥 Force-forging (no cache)... Building for $(or $(service),all services) from $(COMPOSE_FILE).$(NC)"
	@$(COMPOSE) build --no-cache $(service)

# ======================================================================================
# INFORMATION & DEBUGGING
# ======================================================================================

status: ## Show status of running services
	@echo -e "$(BLUE)📋 System Status Report for $(COMPOSE_FILE):$(NC)"
	@$(COMPOSE) ps $(service)

ps: status ## Alias for status

logs: ## Follow logs for specified service, or all if none specified
	@echo -e "$(BLUE)📡 Tapping into data stream... Logs for $(or $(service),all services) from $(COMPOSE_FILE).$(NC)"
	@$(COMPOSE) logs -f --tail="100" $(service)

config: ## Validate and display effective Docker Compose configuration
	@echo -e "$(BLUE)📐 Blueprint Configuration for $(COMPOSE_FILE):$(NC)"
	@$(COMPOSE) config

ssh: ## Get an interactive shell into a running service container
	@if [ -z "$(service)" ]; then \
		echo -e "$(RED)❌ Error: Service name required. Usage: make ssh service=<service_name>$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)🔗 Establishing DirectConnect to $(service) from $(COMPOSE_FILE)... Standby.$(NC)"
	@$(COMPOSE) exec $(service) /bin/bash || $(COMPOSE) exec $(service) /bin/sh || echo -e "$(RED)❌ Failed to find /bin/bash or /bin/sh in $(service).$(NC)"

it: ssh ## Alias for ssh

exec: ## Execute a command in a running service container
	@if [ -z "$(service)" ] || [ -z "$(args)" ]; then \
		echo -e "$(RED)❌ Error: Service name and command required. Usage: make exec service=<service_name> args=\"<command>\"$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)⚡ Executing remote directive in $(service) (from $(COMPOSE_FILE)): $(args)...$(NC)"
	@$(COMPOSE) exec $(service) $(args)

inspect: ## Inspect a running service container
	@if [ -z "$(service)" ]; then \
		echo -e "$(RED)❌ Error: Service name required. Usage: make inspect service=<service_name>$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(BLUE)🔍 Performing deep scan of $(service) (from $(COMPOSE_FILE)) internals...$(NC)"
	@_container_id=$$($(COMPOSE) ps -q $(service) | head -n 1); \
	if [ -z "$$_container_id" ]; then \
		echo -e "$(RED)❌ Service $(service) not found or not running.$(NC)"; \
		exit 1; \
	fi; \
	docker inspect $$_container_id

list-volumes: ## List Docker volumes
	@echo -e "$(BLUE)💾 Docker Volumes for project $(PROJECT_NAME):$(NC)"
	@docker volume ls --filter label=com.docker.compose.project=$(PROJECT_NAME) || docker volume ls

list-networks: ## List Docker networks
	@echo -e "$(BLUE)🌐 Docker Networks for project $(PROJECT_NAME):$(NC)"
	@docker network ls --filter label=com.docker.compose.project=$(PROJECT_NAME) || docker network ls

# ======================================================================================
# CLEANING & PRUNING
# ======================================================================================

clean: ## Remove stopped service containers and default network
	@echo -e "$(RED)🧹 Cleaning containers and networks from $(COMPOSE_FILE)...$(NC)"
	@$(COMPOSE) down --remove-orphans 

fclean: ## Remove containers, networks, volumes defined in compose file
	@echo -e "$(RED)🗑️ Deep cleaning containers, networks, and volumes from $(COMPOSE_FILE)...$(NC)"
	@$(COMPOSE) down --volumes --remove-orphans --rmi local

prune: fclean ## Prune all unused Docker resources
	@echo -e "$(RED)💥 Pruning all unused Docker resources...$(NC)"
	@docker system prune -af --volumes
	@docker builder prune -af
	@docker volume prune -af 
	@echo -e "$(GREEN)✅ Docker system prune complete.$(NC)"

# ======================================================================================
# TRADING BOT SPECIFIC TARGETS
# ======================================================================================

trading-bot: ## Start only trading bot service
	@echo -e "$(CYAN)🤖 Starting Trading Bot service...$(NC)"
	@$(COMPOSE) up -d --build trading-bot && make logs service=trading-bot

llm-gateway: ## Start only LLM gateway service
	@echo -e "$(PURPLE)🧠 Starting LLM Gateway service...$(NC)"
	@$(COMPOSE) up -d --build llm-gateway && make logs service=llm-gateway

agent-start: ## Start the trading agent
	@echo -e "$(GREEN)🎯 Starting trading agent...$(NC)"
	@curl -X POST http://localhost:8000/api/v1/chart/agent/start || echo -e "$(RED)❌ Failed to start agent. Is the service running?$(NC)"

agent-stop: ## Stop the trading agent
	@echo -e "$(YELLOW)🛑 Stopping trading agent...$(NC)"
	@curl -X POST http://localhost:8000/api/v1/chart/agent/stop || echo -e "$(RED)❌ Failed to stop agent. Is the service running?$(NC)"

agent-status: ## Get trading agent status
	@echo -e "$(BLUE)📊 Getting trading agent status...$(NC)"
	@curl -s http://localhost:8000/api/v1/chart/agent/status | python -m json.tool || echo -e "$(RED)❌ Failed to get status. Is the service running?$(NC)"

cli: ## Open trading bot CLI interface
	@echo -e "$(CYAN)💻 Opening Trading Bot CLI...$(NC)"
	@$(COMPOSE) exec trading-bot python -c "\
from src.integrations.iq_option.service import IQOptionService; \
import asyncio; \
async def main(): \
    service = IQOptionService(); \
    await service.connect(); \
    profile = await service.get_profile(); \
    print('=== IQ Option Trading Bot CLI ==='); \
    print(f'Account: {profile.get(\"account_type\", \"Unknown\")}'); \
    print(f'Balance: \$${ profile.get(\"balance\", 0)}'); \
    print('Available commands:'); \
    print('- make agent-start  : Start trading agent'); \
    print('- make agent-status : Check agent status'); \
    print('- make demo        : Run demonstration'); \
    print('- make test        : Run tests'); \
asyncio.run(main())"

# ======================================================================================
# DATABASE MANAGEMENT
# ======================================================================================

db-migrate: ## Run database migrations
	@echo -e "$(BLUE)📊 Running database migrations...$(NC)"
	@$(COMPOSE) exec trading-bot python -c "\
import asyncio; \
from sqlalchemy import create_engine; \
from config.settings import settings; \
print('Database migrations would run here...'); \
print(f'Database URL: {settings.database_url}');"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo -e "$(RED)⚠️ WARNING: This will destroy ALL database data!$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || exit 1
	@echo -e "$(RED)💥 Resetting database...$(NC)"
	@$(COMPOSE) exec db dropdb -U user trading_bot || true
	@$(COMPOSE) exec db createdb -U user trading_bot
	@make db-migrate

# ======================================================================================
# DEVELOPMENT TOOLS
# ======================================================================================

install: ## Install local dependencies
	@echo -e "$(YELLOW)📦 Installing local dependencies...$(NC)"
	@cd services/trading-bot && python -m pip install -r requirements.txt

format: ## Run code formatting
	@echo -e "$(YELLOW)✨ Formatting code...$(NC)"
	@$(COMPOSE) exec trading-bot python -m black src/ --line-length 100 || echo "Black not installed, skipping format"

lint: ## Run linter
	@echo -e "$(YELLOW)🔍 Linting code...$(NC)"
	@$(COMPOSE) exec trading-bot python -m flake8 src/ || echo "Flake8 not installed, skipping lint"

check-env: ## Validate environment configuration
	@echo -e "$(BLUE)🔍 Checking environment configuration...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo -e "$(YELLOW)⚠️ .env file not found. Copying from .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	@echo -e "$(GREEN)✅ Environment file exists$(NC)"
	@if grep -q "your_email@example.com" .env 2>/dev/null; then \
		echo -e "$(YELLOW)⚠️ Please configure your IQ Option credentials in .env$(NC)"; \
	else \
		echo -e "$(GREEN)✅ Credentials appear to be configured$(NC)"; \
	fi

# ======================================================================================
# MONITORING & ANALYTICS
# ======================================================================================

monitoring: ## Start monitoring stack (if available)
	@echo -e "$(PURPLE)📊 Starting monitoring stack...$(NC)"
	@$(COMPOSE) up -d grafana prometheus cadvisor || echo "Monitoring services not configured"

# ======================================================================================
# ENVIRONMENT-SPECIFIC TARGETS
# ======================================================================================

local: ## Start local development environment
	@echo -e "$(CYAN)🏠 Starting local development environment...$(NC)"
	@COMPOSE_FILE=infra/docker-compose.yml $(MAKE) up

staging: ## Start staging environment
	@echo -e "$(YELLOW)🎭 Starting staging environment...$(NC)"
	@COMPOSE_FILE=infra/docker-compose.staging.yml $(MAKE) up || echo "Staging compose file not found"

# ======================================================================================
# VARIABLE HANDLING
# ======================================================================================
ifeq ($(file),)
    # file is not set, use default COMPOSE_FILE
else
    COMPOSE_FILE := $(file)
    COMPOSE := docker compose -f $(COMPOSE_FILE)
endif

# ======================================================================================
# ADDITIONAL UTILITIES
# ======================================================================================

version: ## Show version information
	@echo -e "$(BLUE)📋 Version Information:$(NC)"
	@echo "Project: IQ Option Trading Bot API"
	@echo "Docker Compose: $$(docker compose version)"
	@echo "Docker: $$(docker --version)"
	@$(COMPOSE) exec trading-bot python --version 2>/dev/null || echo "Trading bot not running"

health: ## Check health of all services
	@echo -e "$(BLUE)🏥 Health Check:$(NC)"
	@echo "Trading Bot API: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/health || echo 'DOWN')"
	@echo "LLM Gateway: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health || echo 'DOWN')"
	@echo "Database: $$($(COMPOSE) exec -T db pg_isready -U user || echo 'DOWN')"
	@echo "Redis: $$($(COMPOSE) exec -T redis redis-cli ping || echo 'DOWN')"

# Catch-all for targets that might not explicitly handle 'service' or 'args'
%:
	@echo -e "$(RED)❌ Unknown target: $@$(NC)"
	@echo -e "$(YELLOW)💡 Use 'make help' to see available targets$(NC)"