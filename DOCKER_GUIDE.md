# 🐳 Docker Containerization Guide

## Overview

This guide provides a complete Docker-based containerization solution for the IQ Option Trading Bot API, following enterprise-grade practices with multi-environment support, monitoring, and scaling capabilities.

## 🚀 Quick Start

### One-Command Setup
```bash
# Automated setup (recommended)
./docker-setup.sh

# Or step-by-step with Makefile
make setup
```

### Manual Setup
```bash
# 1. Check prerequisites
make check-env

# 2. Build images
make build

# 3. Start services
make up

# 4. View logs
make logs

# 5. Check status
make status
```

## 📁 Project Structure

```
├── infra/                          # Infrastructure configuration
│   ├── docker-compose.yml          # Main compose file
│   ├── docker-compose.dev.yml      # Development environment
│   ├── docker-compose.prod.yml     # Production environment
│   ├── nginx/                      # Reverse proxy config
│   ├── redis/                      # Redis configuration
│   ├── sql/                        # Database initialization
│   └── monitoring/                 # Monitoring stack
├── services/
│   ├── trading-bot/                # Main trading service
│   │   ├── Dockerfile              # Production image
│   │   ├── Dockerfile.dev          # Development image
│   │   └── requirements.txt        # Python dependencies
│   └── llm_gateway/               # LLM service
├── docker-setup.sh               # Automated setup script
├── Makefile                       # Container management
└── README.md                      # This file
```

## 🛠️ Make Commands (Your Style)

### 🎯 Quick Start Commands
- `make setup` - Complete setup (install deps, build, start)
- `make app` - Start complete trading application stack
- `make dev` - Start development environment with hot reload
- `make prod` - Start production environment
- `make demo` - Run system demonstration
- `make test` - Run comprehensive test suite

### 🐳 Core Stack Management
- `make up` - Start all services in detached mode
- `make down` - Stop and remove all services
- `make restart` - Restart all services (down + up)
- `make re` - Rebuild images and restart all services
- `make rere` - Rebuild images without cache and restart all services
- `make stop` - Stop all services without removing them

### 🏗️ Building Images
- `make build [service=<name>]` - Build images (all or specific service)
- `make no-cache [service=<name>]` - Build images without cache

### 📊 Information & Debugging
- `make status [service=<name>]` - Show status of services (Alias: ps)
- `make logs [service=<name>]` - Follow logs (all or specific service)
- `make config` - Validate and display effective Docker Compose configuration
- `make ssh service=<name>` - Get an interactive shell into a running service
- `make exec service=<name> args="<cmd>"` - Execute a command in a running service
- `make inspect service=<name>` - Inspect a running service container

### 🧹 Cleaning & Pruning
- `make clean` - Remove stopped service containers and networks
- `make fclean` - Deep clean: containers, networks, volumes, and images
- `make prune` - Prune all unused Docker resources

### 🤖 Trading Bot Specific
- `make trading-bot` - Start only trading bot service
- `make llm-gateway` - Start only LLM gateway service
- `make agent-start` - Start the trading agent
- `make agent-stop` - Stop the trading agent
- `make agent-status` - Get trading agent status
- `make cli` - Open trading bot CLI interface

### 💾 Database Management
- `make db-migrate` - Run database migrations
- `make db-reset` - Reset database (WARNING: destroys all data)

### 🔧 Development Tools
- `make install` - Install local dependencies
- `make format` - Run code formatting
- `make lint` - Run linter
- `make check-env` - Validate environment configuration

## 🌍 Environment Support

### Development Environment
```bash
# Start development environment with hot reload and debugging tools
make dev

# Or use the setup script
./docker-setup.sh dev
```

**Features:**
- ✅ Hot reload for code changes
- ✅ Debug port (5678) exposed
- ✅ Development tools (Adminer, Redis Insight, Mailhog)
- ✅ Verbose logging
- ✅ Source code mounted for live editing

**Available Tools:**
- **Adminer** (Database UI): http://localhost:8080
- **Redis Insight**: http://localhost:8081
- **Mailhog** (Email testing): http://localhost:8025
- **Debug Port**: 5678

### Production Environment
```bash
# Start production environment with monitoring and scaling
make prod

# Or use the setup script
./docker-setup.sh prod
```

**Features:**
- ✅ Optimized Docker images
- ✅ Health checks and auto-restart
- ✅ Monitoring stack (Prometheus, Grafana)
- ✅ SSL/TLS support
- ✅ Load balancing with NGINX
- ✅ Resource limits and scaling
- ✅ Security hardening

**Monitoring Stack:**
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **cAdvisor**: http://localhost:8080

## 📦 Services Architecture

### Core Services

#### 🤖 Trading Bot (`trading-bot`)
- **Port**: 8000
- **Purpose**: Main API server with IQ Option integration
- **Health**: `http://localhost:8000/api/v1/health`
- **Docs**: `http://localhost:8000/api/v1/docs`

#### 🧠 LLM Gateway (`llm-gateway`)
- **Port**: 8001
- **Purpose**: AI/ML service for trading decisions
- **Health**: `http://localhost:8001/health`
- **Docs**: `http://localhost:8001/docs`

#### 💾 PostgreSQL (`db`)
- **Port**: 5432
- **Purpose**: Persistent data storage
- **Database**: `trading_bot`
- **Health**: `pg_isready` check

#### 🗄️ Redis (`redis`)
- **Port**: 6379
- **Purpose**: Caching and message queues
- **Health**: `redis-cli ping`

#### 🧠 Ollama (`ollama`)
- **Port**: 11434
- **Purpose**: Local LLM inference
- **Optional**: Disable for production

#### 🌐 NGINX (`nginx`)
- **Port**: 80, 443
- **Purpose**: Reverse proxy and load balancer
- **Features**: SSL termination, rate limiting, compression

## 🔧 Configuration

### Environment Variables (.env)
```bash
# IQ Option API Credentials
IQ_OPTION_EMAIL=your_email@example.com
IQ_OPTION_PASSWORD=your_password

# Database
POSTGRES_PASSWORD=secure_password

# Security
SECRET_KEY=your_secret_key

# Trading Configuration
TRADING_MODE=demo  # demo/live
LOG_LEVEL=INFO
```

### Docker Compose Files
- **`docker-compose.yml`** - Production-ready base configuration
- **`docker-compose.dev.yml`** - Development with hot reload and tools
- **`docker-compose.prod.yml`** - Production with monitoring and scaling
- **`docker-compose.test.yml`** - Testing environment

## 🔒 Security Features

### Development Security
- ✅ Non-root containers
- ✅ Network isolation
- ✅ Volume permissions
- ✅ Development-specific secrets

### Production Security
- ✅ SSL/TLS encryption
- ✅ Rate limiting
- ✅ Security headers
- ✅ Container scanning
- ✅ Secret management
- ✅ Network policies
- ✅ Resource constraints

## 📊 Monitoring & Observability

### Health Checks
All services include comprehensive health checks:
```bash
# Check all services health
make health

# Individual service health
curl -f http://localhost:8000/api/v1/health  # Trading Bot
curl -f http://localhost:8001/health         # LLM Gateway
```

### Logging
Centralized logging with structured formats:
```bash
# View all logs
make logs

# Service-specific logs
make logs service=trading-bot
make logs service=llm-gateway

# Follow logs in real-time
make logs | grep "ERROR"
```

### Metrics (Production)
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Node Exporter**: System metrics
- **cAdvisor**: Container metrics

## 🚀 Deployment Scenarios

### Local Development
```bash
# Quick development setup
./docker-setup.sh dev
make logs

# Make code changes - auto-reload enabled
# Debug with port 5678
```

### Staging Environment
```bash
# Use staging configuration
make up file=infra/docker-compose.staging.yml

# Test with real-like data
make test
```

### Production Deployment
```bash
# Production deployment
./docker-setup.sh prod

# Monitor deployment
make health
make logs

# Scale services
docker compose -f infra/docker-compose.prod.yml up --scale trading-worker=3
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy IQ Option Bot
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          ./docker-setup.sh prod
          make test
```

### GitLab CI Example
```yaml
stages:
  - build
  - test
  - deploy

docker-build:
  stage: build
  script:
    - make build

integration-test:
  stage: test
  script:
    - make test

production-deploy:
  stage: deploy
  script:
    - ./docker-setup.sh prod
  only:
    - main
```

## 🐛 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker daemon
docker info

# Check logs for errors
make logs service=trading-bot

# Rebuild images
make rere
```

#### Database Connection Issues
```bash
# Check database health
make exec service=db args="pg_isready -U user"

# View database logs
make logs service=db

# Reset database (WARNING: destroys data)
make db-reset
```

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8000

# Use different ports in compose file
# Or stop conflicting services
```

#### Memory Issues
```bash
# Check container resource usage
docker stats

# Increase Docker memory limits
# Clean up unused resources
make prune
```

### Debug Mode
```bash
# Start with debug logging
LOG_LEVEL=DEBUG make up

# Access container shell
make ssh service=trading-bot

# Run interactive debugging
make exec service=trading-bot args="python -c 'import pdb; pdb.set_trace()'"
```

## 📈 Performance Optimization

### Resource Limits
Configure in `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Scaling
```bash
# Scale trading workers
docker compose up --scale trading-worker=3

# Load balance with NGINX
# Monitor with Grafana dashboards
```

### Caching
- Redis for API responses
- NGINX for static content
- Application-level caching

## 🔗 Integration Examples

### With External Monitoring
```bash
# Add external monitoring
docker compose -f docker-compose.yml -f monitoring/external.yml up
```

### With Load Balancer
```bash
# Use external load balancer
make up
# Configure load balancer to point to multiple instances
```

### With Container Orchestration
```bash
# Kubernetes deployment
kubectl apply -f k8s/

# Docker Swarm
docker stack deploy -c docker-compose.yml iq-bot
```

## 📚 Additional Resources

- **Make Help**: `make help` - Full command reference
- **Configuration Guide**: `IMPLEMENTATION_SUMMARY.md`
- **IQ Option Setup**: `IQ_OPTION_INTEGRATION.md`
- **API Documentation**: http://localhost:8000/api/v1/docs (when running)
- **Docker Best Practices**: Official Docker documentation

---

## 🎯 Quick Reference Card

| Command | Description |
|---------|-------------|
| `./docker-setup.sh` | Complete automated setup |
| `make setup` | Manual complete setup |
| `make app` | Start trading application |
| `make dev` | Development environment |
| `make logs` | View all logs |
| `make ssh service=trading-bot` | Shell into container |
| `make agent-start` | Start trading agent |
| `make agent-status` | Check agent status |
| `make demo` | Run system demo |
| `make clean` | Clean up containers |

**🎉 Ready to trade in containers! 🚀**