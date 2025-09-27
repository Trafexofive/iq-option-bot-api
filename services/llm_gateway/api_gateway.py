# ======================================================================================
# LLM API Gateway - Final Version (Stream-Fixed)
# Description: Contains all required endpoints, including /health and /providers,
# with resilient, non-blocking provider initialization.
# ======================================================================================

import os
import logging
import random
from typing import Dict, List, Optional
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from provider_base import LLMProvider, CompletionRequest, CompletionResponse, Message
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider
from providers.ollama_provider import OllamaProvider
from providers.github_models_provider import GitHubModelsProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_gateway")

app = FastAPI(title="LLM API Gateway", version="2.2.1")
providers: Dict[str, LLMProvider] = {}

class CompletionRequestAPI(BaseModel):
    provider: Optional[str] = None
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    fallback: bool = True
    stream: bool = False

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing providers based on environment flags...")
    if os.getenv('ENABLE_GEMINI', 'false').lower() == 'true' and os.getenv("GEMINI_API_KEY"):
        providers["gemini"] = GeminiProvider()
        logger.info("Gemini provider instance created.")
    if os.getenv('ENABLE_GROQ', 'false').lower() == 'true' and os.getenv("GROQ_API_KEY"):
        providers["groq"] = GroqProvider()
        logger.info("Groq provider instance created.")
    if os.getenv('ENABLE_GITHUB_MODELS', 'false').lower() == 'true' and os.getenv("GITHUB_TOKEN"):
        providers["github_models"] = GitHubModelsProvider()
        logger.info("GitHub Models provider instance created.")
    if os.getenv('ENABLE_OLLAMA', 'true').lower() == 'true':
        providers["ollama"] = OllamaProvider()
        logger.info("Ollama provider instance created.")
    logger.info(f"Startup complete. Configured providers: {list(providers.keys())}")

@app.get("/health", status_code=200, tags=["Gateway"])
async def health_check():
    """A simple, non-blocking health check endpoint for Docker.""" 
    return {"status": "healthy", "active_providers": list(providers.keys())}

@app.get("/providers", tags=["Gateway"])
async def list_providers():
    """Lists all configured providers and their runtime availability."""
    details = {}
    for name, p in providers.items():
        details[name] = {"available": await p.is_available()}
    return details

@app.post("/completion", tags=["LLM"])
async def get_completion(request: CompletionRequestAPI):
    available_providers = [name for name, p in providers.items() if await p.is_available()]
    if not available_providers:
        raise HTTPException(status_code=503, detail="No LLM providers are currently available.")
    
    provider_name = request.provider if request.provider in available_providers else random.choice(available_providers)
    
    provider_request = CompletionRequest(**request.dict())

    async def stream_generator():
        try:
            async for chunk in providers[provider_name].get_streaming_completion(provider_request):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Provider '{provider_name}' failed during stream: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    if request.stream:
        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        try:
            return await providers[provider_name].get_completion(provider_request)
        except Exception as e:
            logger.error(f"Provider '{provider_name}' failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
