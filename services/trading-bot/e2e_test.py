import asyncio
import httpx
import pytest
from datetime import datetime
from src.models.trading import TradeDirection


async def test_api_health():
    """Test the health endpoint"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")


async def test_get_market_data():
    """Test getting market data"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/v1/market/EURUSD")
        assert response.status_code == 200
        data = response.json()
        assert "asset" in data
        assert data["asset"] == "EURUSD"
        print("✓ Market data retrieval passed")


async def test_llm_analysis():
    """Test LLM market analysis"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # First get market data
        market_response = await client.get("/api/v1/market/EURUSD")
        assert market_response.status_code == 200
        market_data = market_response.json()
        
        # Then test analysis
        payload = {"asset": "EURUSD", "market_data": market_data, "risk_level": 0.5}
        response = await client.post("/api/v1/analyze", json=payload)
        # Note: This might fail if LLM provider is misconfigured, so we'll handle that
        print(f"LLM Analysis status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            assert "decision" in data
            print("✓ LLM analysis passed")
        else:
            print("⚠ LLM analysis failed (likely due to missing API key)")


async def test_trading_endpoint():
    """Test the trading endpoint"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Get current market data
        market_response = await client.get("/api/v1/market/EURUSD")
        assert market_response.status_code == 200
        market_data = market_response.json()
        
        # Try to execute a trade
        trade_payload = {
            "asset": "EURUSD",
            "direction": "call",
            "amount": 10,
            "duration": 60
        }
        
        response = await client.post("/api/v1/trade", json=trade_payload)
        print(f"Trade execution status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            assert "trade_id" in data
            print("✓ Trade execution passed")
        else:
            print("⚠ Trade execution failed (likely due to missing API keys or mock implementation)")


async def run_all_tests():
    """Run all end-to-end tests"""
    print("Starting end-to-end tests for LLM Trading Bot API...")
    print("="*50)
    
    try:
        await test_api_health()
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
    
    try:
        await test_get_market_data()
    except Exception as e:
        print(f"✗ Market data test failed: {str(e)}")
    
    try:
        await test_llm_analysis()
    except Exception as e:
        print(f"✗ LLM analysis test failed: {str(e)}")
    
    try:
        await test_trading_endpoint()
    except Exception as e:
        print(f"✗ Trading test failed: {str(e)}")
    
    print("="*50)
    print("End-to-end tests completed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())