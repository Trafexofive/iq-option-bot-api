#!/usr/bin/env python3
"""
Test script to verify LLM Gateway integration
This script tests the connection between services and providers
"""

import asyncio
import httpx
import sys
import json
from datetime import datetime


async def test_llm_gateway():
    """Test LLM Gateway functionality"""
    
    print("🧪 Testing LLM Gateway Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   📋 Active providers: {health_data['active_providers']}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
        
        # Test 2: List providers
        print("\n2. Testing providers endpoint...")
        try:
            response = await client.get(f"{base_url}/providers")
            providers_data = response.json()
            
            available_providers = []
            for provider, info in providers_data.items():
                status = "✅" if info['available'] else "❌"
                print(f"   {status} {provider}: {'Available' if info['available'] else 'Unavailable'}")
                if info['available']:
                    available_providers.append(provider)
                    
        except Exception as e:
            print(f"   ❌ Providers check failed: {e}")
            return False
        
        # Test 3: Try a simple completion with each available provider
        print("\n3. Testing completion endpoint...")
        
        test_messages = [
            {"role": "user", "content": "Reply with just 'OK' and nothing else."}
        ]
        
        successful_providers = []
        
        for provider in available_providers:
            print(f"\n   Testing {provider} provider...")
            try:
                completion_data = {
                    "provider": provider,
                    "messages": test_messages,
                    "temperature": 0.1,
                    "max_tokens": 10
                }
                
                response = await client.post(
                    f"{base_url}/completion",
                    json=completion_data,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('content', 'No content')
                    print(f"   ✅ {provider}: {content[:50]}{'...' if len(content) > 50 else ''}")
                    successful_providers.append(provider)
                else:
                    print(f"   ❌ {provider}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {provider}: {str(e)[:100]}...")
        
        # Test 4: Trading-specific test
        print(f"\n4. Testing trading analysis...")
        if successful_providers:
            provider = successful_providers[0]  # Use first working provider
            
            market_data = {
                "price": 1.0850,
                "timestamp": datetime.now().isoformat(),
                "volume": 1000
            }
            
            trading_prompt = f"""Based on EURUSD market data: price={market_data['price']}, 
should I place a CALL or PUT trade? Reply with just 'CALL' or 'PUT'."""
            
            try:
                completion_data = {
                    "provider": provider,
                    "messages": [{"role": "user", "content": trading_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 20
                }
                
                response = await client.post(f"{base_url}/completion", json=completion_data)
                result = response.json()
                recommendation = result.get('content', 'No recommendation')
                
                print(f"   ✅ Trading analysis from {provider}: {recommendation}")
                
            except Exception as e:
                print(f"   ❌ Trading analysis failed: {e}")
        else:
            print("   ⚠️  No working providers for trading analysis")
    
    print(f"\n🏁 Test completed!")
    print(f"   Working providers: {len(successful_providers)}/{len(available_providers)}")
    print(f"   Providers: {successful_providers}")
    
    return len(successful_providers) > 0


async def test_microservice_integration():
    """Test integration between trading bot and LLM gateway"""
    
    print("\n🔗 Testing Microservice Integration")
    print("=" * 50)
    
    # Simulate what the trading bot would do
    try:
        # Import the LLM service client
        sys.path.append('/home/mlamkadm/repos/iq-option-bot-api/services/trading-bot/src')
        from integrations.llm_service import LLMServiceClient
        
        # Create client instance
        llm_client = LLMServiceClient("http://localhost:8001")
        
        # Test health
        print("1. Testing LLM service health...")
        health = await llm_client.health_check()
        print(f"   ✅ LLM service healthy: {health['status']}")
        
        # Test providers
        print("2. Testing provider listing...")
        providers = await llm_client.list_providers()
        working_providers = [p for p, info in providers.items() if info['available']]
        print(f"   ✅ Available providers: {working_providers}")
        
        # Test trading analysis
        print("3. Testing trading analysis...")
        mock_market_data = {
            "price": 1.0850,
            "timestamp": datetime.now().isoformat(),
            "volume": 1200,
            "change_24h": 0.0025
        }
        
        analysis = await llm_client.get_trading_analysis(mock_market_data, "EURUSD")
        print(f"   ✅ Trading analysis:")
        print(f"      Direction: {analysis['direction']}")
        print(f"      Confidence: {analysis['confidence']}/10")
        print(f"      Reasoning: {analysis['reasoning']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False


async def main():
    """Run all tests"""
    
    print("🚀 IQ Option Bot - LLM Gateway Integration Tests")
    print("=" * 60)
    
    # Test 1: Direct LLM Gateway tests  
    gateway_success = await test_llm_gateway()
    
    # Test 2: Microservice integration
    integration_success = await test_microservice_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   LLM Gateway: {'✅ PASS' if gateway_success else '❌ FAIL'}")
    print(f"   Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if gateway_success and integration_success:
        print("\n🎉 All tests passed! System is ready for trading.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)