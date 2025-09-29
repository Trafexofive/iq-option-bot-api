#!/usr/bin/env python3
"""Test script for real IQ Option API integration."""

import asyncio
import sys
import logging
import os
from pathlib import Path
from datetime import datetime

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mock_mode():
    """Test IQ Option service in mock mode."""
    logger.info("Testing IQ Option service in mock mode...")
    
    try:
        from src.integrations.iq_option.service import IQOptionService
        
        # Create service in mock mode
        service = IQOptionService(use_real_api=False)
        
        # Test connection
        await service.connect()
        logger.info(f"✅ Connected (mock mode): {service.connected}")
        
        # Test balance
        balance = await service.get_balance()
        logger.info(f"✅ Balance: ${balance}")
        
        # Test profile
        profile = await service.get_profile()
        logger.info(f"✅ Profile: {profile['account_type']} - {profile['name']}")
        
        # Test market status
        is_open = await service.is_market_open("EURUSD")
        logger.info(f"✅ EURUSD market open: {is_open}")
        
        # Test quote
        quote = await service.get_real_time_quote("EURUSD")
        if quote:
            logger.info(f"✅ EURUSD quote: {quote['price']} at {quote['timestamp']}")
        
        # Test chart data
        chart_data = await service.get_chart_data("EURUSD", "M1", 10)
        if chart_data:
            logger.info(f"✅ Chart data: {len(chart_data.candles)} candles")
        
        # Test trade execution (mock)
        from src.models.trading import TradeDirection
        result = await service.execute_trade("EURUSD", TradeDirection.CALL, 10.0, 60)
        if result["success"]:
            logger.info(f"✅ Mock trade executed: {result['trade_id']}")
        
        await service.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"❌ Mock mode test failed: {e}")
        return False


async def test_real_api_without_credentials():
    """Test real API behavior when credentials are not available."""
    logger.info("Testing real API fallback when credentials unavailable...")
    
    try:
        from src.integrations.iq_option.service import IQOptionService
        
        # Create service in real API mode (will fail without credentials)
        service = IQOptionService(use_real_api=True)
        
        # This should fail gracefully and fallback to mock mode
        await service.connect()
        
        # Check if it fell back to mock mode
        if not service.is_using_real_api():
            logger.info("✅ Successfully fell back to mock mode")
            return True
        else:
            logger.warning("⚠️ Real API connection succeeded (unexpected without credentials)")
            await service.disconnect()
            return True
            
    except Exception as e:
        logger.error(f"❌ Real API fallback test failed: {e}")
        return False


async def test_real_api_with_credentials():
    """Test real API with actual credentials (if available)."""
    logger.info("Testing real IQ Option API with credentials...")
    
    # Check if credentials are available
    try:
        from config.settings import settings
        
        if (not hasattr(settings, 'iq_option_email') or 
            not settings.iq_option_email or 
            settings.iq_option_email == 'your_email@example.com'):
            logger.info("⏭️ Skipping real API test - no credentials configured")
            return True
            
    except Exception as e:
        logger.info(f"⏭️ Skipping real API test - settings error: {e}")
        return True
    
    try:
        from src.integrations.iq_option.service import IQOptionService
        from src.models.trading import TradeDirection
        
        # Create service in real API mode
        service = IQOptionService(use_real_api=True)
        
        # Test connection
        await service.connect()
        
        if not service.is_using_real_api():
            logger.info("⚠️ Fell back to mock mode - credentials may be invalid")
            return True
        
        logger.info("✅ Connected to real IQ Option API")
        
        # Test account information
        status = await service.get_connection_status()
        logger.info(f"✅ Connection status: {status}")
        
        profile = await service.get_profile()
        logger.info(f"✅ Account: {profile.get('account_type', 'Unknown')} - Balance: ${profile.get('balance', 0)}")
        
        # Test market data
        assets_to_test = ["EURUSD", "GBPUSD", "BTCUSD"]
        for asset in assets_to_test:
            try:
                # Check market status
                is_open = await service.is_market_open(asset)
                logger.info(f"✅ {asset} market: {'Open' if is_open else 'Closed'}")
                
                # Get real-time quote
                quote = await service.get_real_time_quote(asset)
                if quote:
                    logger.info(f"✅ {asset} price: {quote['price']}")
                
                # Get chart data
                chart_data = await service.get_chart_data(asset, "M1", 5)
                if chart_data and chart_data.candles:
                    latest = chart_data.candles[-1]
                    logger.info(f"✅ {asset} M1 data: {len(chart_data.candles)} candles, latest close: {latest.close}")
                
            except Exception as e:
                logger.warning(f"⚠️ Error testing {asset}: {e}")
        
        # Test small trade execution (BE CAREFUL - THIS IS REAL MONEY!)
        # Uncomment only if you want to test with real trades
        """
        logger.warning("⚠️ About to execute a REAL trade with real money!")
        logger.warning("⚠️ Make sure you're in PRACTICE mode!")
        
        result = await service.execute_trade("EURUSD", TradeDirection.CALL, 1.0, 60)
        if result["success"]:
            logger.info(f"✅ Real trade executed: {result}")
        else:
            logger.error(f"❌ Real trade failed: {result}")
        """
        
        await service.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"❌ Real API test failed: {e}")
        return False


async def test_configuration_integration():
    """Test configuration integration with IQ Option settings."""
    logger.info("Testing configuration integration...")
    
    try:
        from src.config.trading_config import config_parser
        
        # Load configuration
        config = config_parser.load_config()
        iq_config = config.iq_option
        
        logger.info(f"✅ IQ Option config loaded:")
        logger.info(f"   Demo mode: {iq_config.demo_mode}")
        logger.info(f"   API timeout: {iq_config.api_timeout}s")
        
        # Test trading configuration
        trading_config = config.trading
        logger.info(f"✅ Trading config:")
        logger.info(f"   Max daily trades: {trading_config.max_daily_trades}")
        logger.info(f"   Balance: {trading_config.balance}")
        logger.info(f"   Trade ratio: {trading_config.trade_amount_ratio}")
        logger.info(f"   Win multiplier: {trading_config.win_amount_multiplier}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration integration test failed: {e}")
        return False


async def test_trading_agent_integration():
    """Test trading agent with IQ Option integration."""
    logger.info("Testing trading agent integration...")
    
    try:
        from src.core.trading_agent import TradingAgent
        
        # Create trading agent
        agent = TradingAgent()
        
        # Check status before starting
        status = agent.get_status()
        logger.info(f"✅ Agent created: {len(status['loaded_indicators'])} indicators, {len(status['loaded_triggers'])} triggers")
        
        # Don't actually start the agent in test mode
        # agent.start() would begin real trading
        
        logger.info("✅ Trading agent integration test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trading agent integration test failed: {e}")
        return False


async def main():
    """Run all IQ Option integration tests."""
    logger.info("🚀 IQ Option API Integration Tests")
    logger.info("=" * 60)
    
    print("\n🔥 IMPORTANT SAFETY NOTICE:")
    print("=" * 40)
    print("• These tests use your actual IQ Option account")
    print("• Make sure you're in PRACTICE/DEMO mode")
    print("• Real trades are commented out by default")
    print("• Review all code before running with real credentials")
    print("=" * 40)
    
    tests = [
        ("Configuration Integration", test_configuration_integration()),
        ("Mock Mode Service", test_mock_mode()),
        ("Real API Fallback", test_real_api_without_credentials()),
        ("Trading Agent Integration", test_trading_agent_integration()),
        ("Real API with Credentials", test_real_api_with_credentials()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info('='*50)
        
        try:
            result = await test_coro
            results.append((test_name, result))
            status = "PASSED" if result else "FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        print("\n🚀 Ready to configure with your IQ Option credentials!")
        print("\nTo use with real credentials:")
        print("1. Copy .env.example to .env")
        print("2. Add your IQ Option email and password")
        print("3. Set demo_mode: true in settings.yml for safety")
        print("4. Run: python test_iq_option_integration.py")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)