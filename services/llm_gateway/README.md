# LLM Gateway Service

A unified gateway for multiple Large Language Model providers.

## Supported Providers

- **Gemini** - Google's Gemini API
- **Groq** - Groq's fast inference API  
- **Ollama** - Local model serving
- **GitHub Models** - GitHub's model marketplace

## Features

- **Multi-provider support** - Automatic failover between providers
- **Streaming responses** - Real-time text generation
- **Load balancing** - Distribute requests across providers
- **Health monitoring** - Track provider availability

## Configuration

Set environment variables to enable providers:

```bash
# Enable/disable providers
ENABLE_GEMINI=true
ENABLE_GROQ=true  
ENABLE_GITHUB_MODELS=true
# Ollama is always enabled

# API Keys
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token
OLLAMA_BASE_URL=http://ollama:11434
```

## API Endpoints

### Health Check
```bash
GET /health
```

### List Providers
```bash
GET /providers
```

### Text Completion
```bash
POST /completion
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "provider": "ollama",  // Optional - auto-select if not specified
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

### Streaming Completion
```bash
POST /completion
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Tell me a story"}
  ],
  "stream": true
}
```

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn api_gateway:app --host 0.0.0.0 --port 8001

# Or with Docker
docker build -t llm-gateway .
docker run -p 8001:8001 --env-file .env llm-gateway
```

## Usage Examples

```python
import httpx

async with httpx.AsyncClient() as client:
    # Simple completion
    response = await client.post("http://localhost:8001/completion", json={
        "messages": [{"role": "user", "content": "What is 2+2?"}],
        "temperature": 0.1
    })
    
    # Streaming completion
    async with client.stream("POST", "http://localhost:8001/completion", json={
        "messages": [{"role": "user", "content": "Count to 10"}],
        "stream": True
    }) as stream:
        async for chunk in stream.aiter_text():
            print(chunk, end="")
```