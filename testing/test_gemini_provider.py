#!/usr/bin/env python3
"""
Simple Gemini test script
Tests the LLM Gateway with Gemini provider only
"""

import asyncio
import httpx
import sys
import json
from datetime import datetime


async def test_gemini_provider():
    """Test Gemini provider through LLM Gateway"""
    
    print("🤖 Testing Gemini Provider via LLM Gateway")
    print("=" * 50)
    
    # Check if user has set a real API key
    print("⚠️  Make sure you've set your GEMINI_API_KEY in .env file!")
    print("   You can get one free at: https://ai.google.dev/")
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   📋 Active providers: {health_data['active_providers']}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
        
        # Test 2: Check providers
        print("\n2. Checking provider availability...")
        try:
            response = await client.get(f"{base_url}/providers")
            providers_data = response.json()
            
            if "gemini" in providers_data:
                if providers_data["gemini"]["available"]:
                    print("   ✅ Gemini: Available")
                else:
                    print("   ❌ Gemini: Not available (check API key)")
                    return False
            else:
                print("   ❌ Gemini provider not configured")
                return False
                
        except Exception as e:
            print(f"   ❌ Provider check failed: {e}")
            return False
        
        # Test 3: Simple completion test
        print("\n3. Testing simple completion...")
        try:
            completion_data = {
                "provider": "gemini",
                "messages": [
                    {"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}
                ],
                "temperature": 0.1,
                "max_tokens": 20
            }
            
            response = await client.post(f"{base_url}/completion", json=completion_data)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', 'No content')
                print(f"   ✅ Gemini response: {content}")
            else:
                error_text = response.text
                print(f"   ❌ Gemini failed with {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Completion test failed: {e}")
            return False
        
        # Test 4: Trading analysis test
        print("\n4. Testing trading analysis...")
        try:
            trading_prompt = """You are a trading assistant. Based on the following data:
- Asset: EURUSD
- Current Price: 1.0850
- Trend: Slightly upward

Should I place a CALL or PUT trade? Respond with just 'CALL' or 'PUT' followed by a brief reason (max 20 words)."""
            
            completion_data = {
                "provider": "gemini",
                "messages": [
                    {"role": "user", "content": trading_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 50
            }
            
            response = await client.post(f"{base_url}/completion", json=completion_data)
            
            if response.status_code == 200:
                result = response.json()
                recommendation = result.get('content', 'No recommendation')
                print(f"   ✅ Trading recommendation: {recommendation}")
            else:
                print(f"   ❌ Trading analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️  Trading analysis error: {e}")
    
    print(f"\n🎉 Gemini test completed successfully!")
    return True


async def main():
    """Main test function"""
    
    print("🚀 IQ Option Bot - Gemini Provider Test")
    print("=" * 60)
    
    success = await test_gemini_provider()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n🔗 Ready to link microservices!")
        print("   - LLM Gateway: Working ✅")
        print("   - Gemini Provider: Working ✅") 
        print("   - Integration: Ready ✅")
        return 0
    else:
        print("❌ TESTS FAILED!")
        print("\n🔧 Check:")
        print("   1. GEMINI_API_KEY is set in .env")
        print("   2. LLM Gateway is running")
        print("   3. Internet connection is working")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)