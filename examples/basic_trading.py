#!/usr/bin/env python3
"""
Basic trading example for IQ Option Bot API.
This example shows how to use the trading API to place a simple trade.
"""

import httpx
import asyncio
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"


async def main():
    """Demo trading workflow"""
    
    async with httpx.AsyncClient() as client:
        # Check API health
        print("Checking API health...")
        response = await client.get(f"{API_BASE_URL}/health")
        print(f"API Status: {response.json()}")
        
        # Get market data
        print("\nFetching market data...")
        response = await client.get(f"{API_BASE_URL}/market/data?asset=EURUSD")
        market_data = response.json()
        print(f"Current EURUSD price: {market_data.get('price', 'N/A')}")
        
        # Get trading recommendation from LLM
        print("\nGetting AI trading recommendation...")
        llm_request = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Based on current EURUSD market data: {market_data}, should I place a CALL or PUT trade? Provide reasoning."
                }
            ],
            "temperature": 0.3
        }
        
        response = await client.post(f"{API_BASE_URL}/llm/completion", json=llm_request)
        recommendation = response.json()
        print(f"AI Recommendation: {recommendation.get('content', 'N/A')}")
        
        # Place a demo trade (if not in production)
        print("\nPlacing demo trade...")
        trade_request = {
            "asset": "EURUSD",
            "direction": "CALL",  # or "PUT" based on AI recommendation
            "amount": 1.0,
            "expiry_minutes": 5,
            "demo": True
        }
        
        response = await client.post(f"{API_BASE_URL}/trading/trade", json=trade_request)
        trade_result = response.json()
        print(f"Trade placed: {trade_result}")


if __name__ == "__main__":
    print("IQ Option Bot API - Basic Trading Example")
    print("=" * 50)
    asyncio.run(main())