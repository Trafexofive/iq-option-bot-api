# Documentation

## API Endpoints

### Trading Bot API (Port 8000)

#### Health Check
- **GET** `/api/v1/health`
- Returns system health status

#### Market Data  
- **GET** `/api/v1/market/data?asset={asset}`
- Returns current market data for specified asset
- Supported assets: EURUSD, GBPUSD, USDJPY, etc.

#### Trading Operations
- **POST** `/api/v1/trading/trade`
- Places a new trade
- Body: `{"asset": "EURUSD", "direction": "CALL|PUT", "amount": 1.0, "expiry_minutes": 5, "demo": true}`

- **GET** `/api/v1/trading/history`
- Returns trading history

- **GET** `/api/v1/trading/balance`
- Returns account balance

#### LLM Integration
- **POST** `/api/v1/llm/completion`
- Get AI trading recommendation
- Body: `{"messages": [{"role": "user", "content": "..."}], "temperature": 0.3}`

### LLM Gateway API (Port 8001)

#### Health Check
- **GET** `/health`
- Returns gateway health status

#### Providers
- **GET** `/providers`
- Lists available LLM providers and their status

#### Completion
- **POST** `/completion`
- Generate text completion using LLM
- Supports streaming responses
- Body: `{"messages": [...], "temperature": 0.7, "stream": false, "provider": "ollama"}`

## Configuration

### Environment Variables

```bash
# IQ Option API
IQ_OPTION_EMAIL=your_email@example.com
IQ_OPTION_PASSWORD=your_password
IQ_OPTION_DEMO_MODE=true

# LLM Configuration
LLM_PROVIDER=ollama
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OLLAMA_BASE_URL=http://ollama:11434

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_bot

# Redis
REDIS_URL=redis://localhost:6379

# Application
LOG_LEVEL=INFO
DEBUG=false
```

### Service Configuration (settings.yml)

The `settings.yml` file contains global configuration for all services:

- Database connection settings
- Trading parameters (risk limits, etc.)
- LLM gateway configuration
- Logging configuration

## Architecture

### Services Overview

1. **Trading Bot Service** (`services/trading-bot/`)
   - Main API server
   - IQ Option integration
   - Market data processing
   - Trade execution

2. **Trading Worker** (Background service)
   - Asynchronous trade processing
   - Market monitoring
   - Risk management

3. **LLM Gateway** (`services/llm_gateway/`)
   - Multi-provider LLM access
   - Streaming support
   - Load balancing

4. **Infrastructure Services**
   - PostgreSQL database
   - Redis cache/queue
   - Ollama local LLM server

### Data Flow

1. Market data is fetched from IQ Option API
2. Data is processed and stored in PostgreSQL
3. Trading signals are generated using LLM analysis
4. Risk assessment is performed
5. Trades are executed through IQ Option API
6. Results are logged and stored

### Development Workflow

1. **Setup**: Run `scripts/setup.sh`
2. **Development**: Use `make dev` for development mode
3. **Testing**: Run `make test` or `scripts/run_tests.sh`
4. **Deployment**: Use `make up` for production mode

## Security Considerations

- Never commit API keys to version control
- Use demo mode for testing
- Implement proper rate limiting
- Monitor account balance and implement stop-losses
- Use HTTPS in production
- Regularly rotate API keys