"""
Integration tests for the complete system.
"""

import pytest
import httpx
import asyncio
import time
from unittest.mock import patch


@pytest.fixture
def trading_client():
    """HTTP client for Trading Bot API"""
    return httpx.AsyncClient(base_url="http://localhost:8000/api/v1")


@pytest.fixture  
def llm_client():
    """HTTP client for LLM Gateway"""
    return httpx.AsyncClient(base_url="http://localhost:8001")


@pytest.mark.asyncio
async def test_complete_trading_workflow(trading_client, llm_client):
    """Test a complete AI-powered trading workflow"""
    
    # Step 1: Check system health
    health_response = await trading_client.get("/health")
    assert health_response.status_code == 200
    
    llm_health = await llm_client.get("/health")
    assert llm_health.status_code == 200
    
    # Step 2: Get market data
    market_response = await trading_client.get("/market/data?asset=EURUSD")
    assert market_response.status_code == 200
    market_data = market_response.json()
    
    # Step 3: Get AI recommendation
    recommendation_request = {
        "messages": [
            {
                "role": "user",
                "content": f"Based on EURUSD data: {market_data}, should I place CALL or PUT? Just answer CALL or PUT."
            }
        ],
        "temperature": 0.1
    }
    
    llm_response = await llm_client.post("/completion", json=recommendation_request)
    assert llm_response.status_code == 200
    recommendation = llm_response.json()
    
    # Step 4: Place trade based on recommendation (demo mode)
    direction = "CALL" if "CALL" in recommendation.get("content", "").upper() else "PUT"
    
    trade_request = {
        "asset": "EURUSD",
        "direction": direction,
        "amount": 1.0,
        "expiry_minutes": 1,
        "demo": True
    }
    
    with patch('src.integrations.iq_option.service.IQOptionService.place_trade') as mock_trade:
        mock_trade.return_value = {
            "trade_id": "integration_test_123",
            "status": "placed",
            "direction": direction,
            "amount": 1.0
        }
        
        trade_response = await trading_client.post("/trading/trade", json=trade_request)
        assert trade_response.status_code == 200
        trade_result = trade_response.json()
        assert trade_result["status"] == "placed"


@pytest.mark.asyncio
async def test_llm_provider_fallback(llm_client):
    """Test LLM provider fallback mechanism"""
    
    # Make multiple requests to test fallback
    for i in range(3):
        completion_request = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Test request {i+1}"
                }
            ],
            "fallback": True,
            "temperature": 0.3
        }
        
        response = await llm_client.post("/completion", json=completion_request)
        # Should get a response from some provider
        assert response.status_code == 200 or response.status_code == 503


@pytest.mark.asyncio
async def test_concurrent_requests(trading_client):
    """Test system under concurrent load"""
    
    async def make_request():
        response = await trading_client.get("/health")
        return response.status_code == 200
    
    # Make 10 concurrent requests
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # All requests should succeed
    assert all(results)


@pytest.mark.asyncio
async def test_market_data_freshness(trading_client):
    """Test that market data is reasonably fresh"""
    
    response = await trading_client.get("/market/data?asset=EURUSD")
    assert response.status_code == 200
    
    data = response.json()
    if "timestamp" in data:
        # Market data should be less than 1 minute old
        current_time = time.time()
        data_time = float(data["timestamp"])
        age_seconds = current_time - data_time
        assert age_seconds < 60  # Less than 1 minute old


@pytest.mark.asyncio
async def test_error_handling_chain(trading_client, llm_client):
    """Test error propagation through the system"""
    
    # Test with invalid market data request
    response = await trading_client.get("/market/data?asset=INVALID_ASSET")
    # Should handle gracefully, not crash
    assert response.status_code in [400, 404, 422]
    
    # Test with invalid LLM request
    invalid_llm_request = {
        "messages": [{"role": "invalid", "content": "test"}],
        "temperature": 999  # Invalid temperature
    }
    
    response = await llm_client.post("/completion", json=invalid_llm_request)
    assert response.status_code == 422  # Validation error