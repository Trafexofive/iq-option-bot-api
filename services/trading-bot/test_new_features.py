#!/usr/bin/env python3
"""Test script for the new trading features."""

import asyncio
import sys
import logging
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_config_loading():
    """Test configuration loading."""
    logger.info("Testing configuration loading...")
    
    try:
        from src.config.trading_config import config_parser
        
        # Test loading configuration
        config = config_parser.load_config()
        logger.info(f"Loaded config successfully: {config.app.name} v{config.app.version}")
        
        # Test trading config
        trading_config = config_parser.get_trading_config()
        logger.info(f"Trading config: {trading_config.max_daily_trades} max trades, {trading_config.timeframes} timeframes")
        
        # Test validation
        validated_feeds = config_parser.validate_context_feeds(trading_config)
        logger.info(f"Validated context feeds: {validated_feeds}")
        
        validated_triggers = config_parser.validate_triggers(trading_config)
        logger.info(f"Validated triggers: {validated_triggers}")
        
        return True
        
    except Exception as e:
        logger.error(f"Config loading test failed: {e}")
        return False


async def test_chart_data_service():
    """Test chart data service."""
    logger.info("Testing chart data service...")
    
    try:
        from src.integrations.chart_data import ChartDataService
        
        service = ChartDataService()
        
        # Test mock data generation
        chart_data = await service.get_chart_data("EURUSD", "M1", 50)
        
        if chart_data:
            logger.info(f"Fetched {len(chart_data.candles)} candles for EURUSD M1")
            logger.info(f"Latest candle: O={chart_data.candles[-1].open}, C={chart_data.candles[-1].close}")
            return True
        else:
            logger.error("Failed to fetch chart data")
            return False
            
    except Exception as e:
        logger.error(f"Chart data test failed: {e}")
        return False


async def test_manifest_loading():
    """Test manifest loading system."""
    logger.info("Testing manifest loading...")
    
    try:
        from src.core.manifests import manifest_loader
        
        # Test loading built-in indicators
        from src.core.manifests import IndicatorManifest, ManifestType
        
        rsi_manifest = IndicatorManifest(
            name="RSI",
            version="1.0.0",
            description="Built-in RSI indicator",
            type=ManifestType.INDICATOR,
            implementation="RSI",
            outputs=["rsi"]
        )
        
        rsi_component = manifest_loader.load_component(rsi_manifest)
        if rsi_component:
            logger.info(f"Successfully loaded RSI component: {rsi_component.name}")
            
            # Test RSI calculation
            test_data = [1.2000, 1.2010, 1.2005, 1.1995, 1.2020, 1.2015, 1.2025, 1.2030, 1.2020, 1.2040,
                        1.2050, 1.2045, 1.2055, 1.2060, 1.2040, 1.2030, 1.2035, 1.2025, 1.2015, 1.2020]
            
            result = rsi_component.calculate(test_data)
            if result and 'rsi' in result:
                logger.info(f"RSI calculation successful, values count: {len(result['rsi'])}")
                return True
            else:
                logger.error("RSI calculation returned no values")
                return False
        else:
            logger.error("Failed to load RSI component")
            return False
            
    except Exception as e:
        logger.error(f"Manifest loading test failed: {e}")
        return False


async def test_iq_option_service():
    """Test IQ Option service integration."""
    logger.info("Testing IQ Option service...")
    
    try:
        from src.integrations.iq_option.service import IQOptionService
        
        service = IQOptionService()
        
        # Test connection
        await service.connect()
        logger.info("IQ Option service connected")
        
        # Test chart data fetching
        chart_data = await service.get_chart_data("EURUSD", "M5", 20)
        if chart_data:
            logger.info(f"Fetched chart data via IQ service: {len(chart_data.candles)} candles")
        
        # Test multiple assets
        multiple_data = await service.get_multiple_chart_data(
            ["EURUSD", "GBPUSD"], ["M1", "M5"], 10
        )
        if multiple_data:
            logger.info(f"Fetched multiple chart data: {len(multiple_data)} assets")
        
        # Test supported assets
        assets = service.get_supported_assets()
        logger.info(f"Supported assets: {len(assets)} total")
        
        await service.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"IQ Option service test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting comprehensive tests for new trading features...")
    
    tests = [
        ("Configuration Loading", test_config_loading()),
        ("Chart Data Service", test_chart_data_service()),
        ("Manifest Loading", test_manifest_loading()),
        ("IQ Option Service", test_iq_option_service()),
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
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)