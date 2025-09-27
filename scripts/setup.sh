#!/bin/bash

# Setup script for IQ Option Bot API
set -e

echo "🚀 IQ Option Bot API Setup"
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from example..."
    cp services/trading-bot/.env.example .env
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Install Python dependencies (if Python is available)
if command -v python3 &> /dev/null; then
    echo "📦 Installing Python dependencies..."
    python3 -m pip install -r requirements.txt
    echo "✅ Python dependencies installed"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/{sample_trades,market_data}
mkdir -p benchmarking
echo "✅ Directories created"

# Build and start core services
echo "🐳 Starting core infrastructure..."
docker-compose -f infra/docker-compose.core.yml up -d

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your IQ Option credentials"
echo "2. Run: python examples/setup_iq_option.py (for guided setup)"
echo "3. Start all services: make up"
echo "4. View API docs: http://localhost:8000/api/v1/docs"
echo "5. Run example: python examples/basic_trading.py"
echo ""
echo "🔧 Useful commands:"
echo "  make help    - Show all available commands"
echo "  make logs    - View service logs"
echo "  make test    - Run tests"
echo "  make clean   - Clean up everything"