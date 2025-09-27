#!/bin/bash

# Test runner script for IQ Option Bot API
set -e

echo "🧪 Running IQ Option Bot API Tests"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "$message"
    fi
}

# Check if services are running
echo "🔍 Checking if services are running..."
if ! docker-compose -f infra/docker-compose.yml ps | grep -q "Up"; then
    print_status "warning" "Services are not running. Starting them..."
    docker-compose -f infra/docker-compose.yml up -d
    sleep 10
fi

# Run unit tests
echo ""
echo "🔬 Running unit tests..."
if python -m pytest testing/ -v --tb=short; then
    print_status "success" "Unit tests passed"
else
    print_status "error" "Unit tests failed"
    exit 1
fi

# Run integration tests within containers
echo ""
echo "🌐 Running integration tests..."
if docker-compose -f infra/docker-compose.yml exec -T trading-bot pytest tests/ -v; then
    print_status "success" "Integration tests passed"
else
    print_status "error" "Integration tests failed"
    exit 1
fi

# Test API endpoints
echo ""
echo "🔌 Testing API endpoints..."

# Wait for services to be ready
sleep 5

# Test health endpoint
if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
    print_status "success" "Trading Bot API health check passed"
else
    print_status "error" "Trading Bot API health check failed"
    exit 1
fi

# Test LLM Gateway
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    print_status "success" "LLM Gateway health check passed"
else
    print_status "error" "LLM Gateway health check failed"
    exit 1
fi

echo ""
print_status "success" "All tests passed! 🎉"
echo ""
echo "📊 Test Summary:"
echo "  - Unit tests: ✅"
echo "  - Integration tests: ✅" 
echo "  - API health checks: ✅"
echo ""
echo "🔗 Useful links:"
echo "  - Trading Bot API: http://localhost:8000/api/v1/docs"
echo "  - LLM Gateway API: http://localhost:8001/docs"