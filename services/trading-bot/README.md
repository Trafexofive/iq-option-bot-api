# llm-trading-bot

This is an AI-powered trading bot that uses LLMs to make trading decisions.

## Project Structure
```
llm-trading-bot/
├── src/
│   ├── api/                 # FastAPI routes and endpoints
│   ├── core/               # Core business logic
│   │   ├── llm/           # LLM integration and prompt management
│   │   ├── trading/       # Trading logic and strategies
│   │   └── market/        # Market data processing
│   ├── integrations/      # External service integrations
│   │   ├── iq_option/     # IQ Option API wrapper
│   │   └── llm_providers/ # OpenAI, Anthropic, local models
│   ├── models/            # Pydantic models
│   └── utils/             # Shared utilities
├── tests/
├── config/
├── docker/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run with Docker: `docker-compose up`

## Development

Use the Makefile for common tasks:
- `make build` - Build the Docker images
- `make up` - Start the services
- `make down` - Stop the services
- `make logs` - View logs
- `make test` - Run tests