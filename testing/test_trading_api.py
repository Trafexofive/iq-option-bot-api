"""
Integration tests for the IQ Option Trading Bot API.
"""

import pytest
import httpx
import asyncio
from unittest.mock import AsyncMock, patch


@pytest.fixture
def api_client():
    """HTTP client for API testing"""
    return httpx.AsyncClient(base_url="http://localhost:8000/api/v1")


@pytest.mark.asyncio
async def test_health_endpoint(api_client):
    """Test the health check endpoint"""
    response = await api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_market_data_endpoint(api_client):
    """Test market data retrieval"""
    response = await api_client.get("/market/data?asset=EURUSD")
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert "timestamp" in data


@pytest.mark.asyncio
@patch('src.integrations.iq_option.service.IQOptionService.place_trade')
async def test_place_trade_demo(mock_place_trade, api_client):
    """Test placing a demo trade"""
    mock_place_trade.return_value = {
        "trade_id": "test_123",
        "status": "placed",
        "amount": 1.0,
        "asset": "EURUSD"
    }
    
    trade_data = {
        "asset": "EURUSD",
        "direction": "CALL",
        "amount": 1.0,
        "expiry_minutes": 5,
        "demo": True
    }
    
    response = await api_client.post("/trading/trade", json=trade_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "placed"
    assert data["asset"] == "EURUSD"


@pytest.mark.asyncio
async def test_trading_history(api_client):
    """Test retrieving trading history"""
    response = await api_client.get("/trading/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_invalid_trade_data(api_client):
    """Test error handling for invalid trade data"""
    invalid_trade = {
        "asset": "INVALID",
        "direction": "INVALID",
        "amount": -1.0
    }
    
    response = await api_client.post("/trading/trade", json=invalid_trade)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_account_balance(api_client):
    """Test account balance retrieval"""
    response = await api_client.get("/trading/balance")
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "currency" in data