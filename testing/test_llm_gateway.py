"""
Tests for the LLM Gateway service.
"""

import pytest
import httpx
import json
from unittest.mock import AsyncMock, patch


@pytest.fixture
def llm_client():
    """HTTP client for LLM Gateway testing"""
    return httpx.AsyncClient(base_url="http://localhost:8001")


@pytest.mark.asyncio
async def test_llm_health_endpoint(llm_client):
    """Test LLM Gateway health check"""
    response = await llm_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_providers(llm_client):
    """Test listing available LLM providers"""
    response = await llm_client.get("/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Should have at least Ollama provider
    assert "ollama" in data


@pytest.mark.asyncio
async def test_completion_request(llm_client):
    """Test LLM completion request"""
    completion_request = {
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2?"
            }
        ],
        "temperature": 0.3,
        "stream": False
    }
    
    response = await llm_client.post("/completion", json=completion_request)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data


@pytest.mark.asyncio
async def test_streaming_completion(llm_client):
    """Test streaming completion"""
    completion_request = {
        "messages": [
            {
                "role": "user",
                "content": "Count from 1 to 3"
            }
        ],
        "temperature": 0.3,
        "stream": True
    }
    
    async with llm_client.stream("POST", "/completion", json=completion_request) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Read first chunk
        chunk = await response.aiter_text().__anext__()
        assert "data:" in chunk


@pytest.mark.asyncio
async def test_provider_specific_request(llm_client):
    """Test requesting specific provider"""
    completion_request = {
        "provider": "ollama",
        "messages": [
            {
                "role": "user", 
                "content": "Hello"
            }
        ],
        "temperature": 0.3
    }
    
    response = await llm_client.post("/completion", json=completion_request)
    # Should either succeed or return 503 if Ollama is not available
    assert response.status_code in [200, 503]


@pytest.mark.asyncio
async def test_invalid_completion_request(llm_client):
    """Test error handling for invalid requests"""
    invalid_request = {
        "messages": [],  # Empty messages should be invalid
        "temperature": -1.0  # Invalid temperature
    }
    
    response = await llm_client.post("/completion", json=invalid_request)
    assert response.status_code == 422  # Validation error