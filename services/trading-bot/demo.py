#!/usr/bin/env python3
"""Demo script showing the new trading features in action."""

import asyncio
import sys
import json
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

async def demo_chart_data():
    """Demonstrate chart data fetching."""
    print("\n🔥 Chart Data Service Demo")
    print("=" * 50)
    
    from src.integrations.chart_data import ChartDataService
    
    service = ChartDataService()
    
    # Fetch single asset data
    print("📊 Fetching EURUSD M5 data...")
    chart_data = await service.get_chart_data("EURUSD", "M5", 20)
    
    if chart_data:
        print(f"✅ Fetched {len(chart_data.candles)} candles")
        print(f"   Latest: {chart_data.candles[-1].timestamp} - Close: {chart_data.candles[-1].close}")
        
        # Show some statistics
        closes = [c.close for c in chart_data.candles]
        print(f"   Price Range: {min(closes):.5f} - {max(closes):.5f}")
    
    # Fetch multiple assets
    print("\n📈 Fetching multiple assets...")
    multi_data = await service.get_multiple_assets_data(
        ["EURUSD", "GBPUSD"], ["M1", "M5"], 10
    )
    
    for asset, timeframes in multi_data.items():
        print(f"   {asset}:")
        for tf, data in timeframes.items():
            if data:
                print(f"     {tf}: {len(data.candles)} candles")


async def demo_indicators():
    """Demonstrate indicator calculations."""
    print("\n⚙️ Technical Indicators Demo")
    print("=" * 50)
    
    from src.core.manifests import RSIIndicator, MACDIndicator, BollingerBandsIndicator
    
    # Generate sample price data
    sample_prices = [
        1.2000, 1.2010, 1.2005, 1.1995, 1.2020, 1.2015, 1.2025, 1.2030, 1.2020, 1.2040,
        1.2050, 1.2045, 1.2055, 1.2060, 1.2040, 1.2030, 1.2035, 1.2025, 1.2015, 1.2020,
        1.2025, 1.2030, 1.2035, 1.2040, 1.2038, 1.2042, 1.2045, 1.2048, 1.2050, 1.2055
    ]
    
    # RSI Calculation
    print("📊 RSI Indicator:")
    rsi = RSIIndicator({"period": 14})
    rsi_result = rsi.calculate(sample_prices)
    if rsi_result['rsi']:
        print(f"   Latest RSI: {rsi_result['rsi'][-1]:.2f}")
    
    # MACD Calculation  
    print("\n📈 MACD Indicator:")
    macd = MACDIndicator({"fast_period": 12, "slow_period": 26, "signal_period": 9})
    macd_result = macd.calculate(sample_prices)
    if macd_result['macd']:
        print(f"   MACD Line: {macd_result['macd'][-1]:.6f}")
        print(f"   Signal Line: {macd_result['signal'][-1]:.6f}")
        print(f"   Histogram: {macd_result['histogram'][-1]:.6f}")
    
    # Bollinger Bands
    print("\n📊 Bollinger Bands:")
    bb = BollingerBandsIndicator({"period": 20, "std_dev": 2})
    bb_result = bb.calculate(sample_prices)
    if bb_result['upper']:
        print(f"   Upper Band: {bb_result['upper'][-1]:.5f}")
        print(f"   Middle Band: {bb_result['middle'][-1]:.5f}") 
        print(f"   Lower Band: {bb_result['lower'][-1]:.5f}")


async def demo_triggers():
    """Demonstrate trigger evaluation."""
    print("\n🎯 Trading Triggers Demo")
    print("=" * 50)
    
    from src.core.manifests import PriceActionTrigger, VolumeSpikeTrigger
    
    # Mock market data
    mock_candles = [
        {"close": 1.2000, "volume": 1500},
        {"close": 1.2010, "volume": 1600}, 
        {"close": 1.2020, "volume": 2100},  # Volume spike + price up
        {"close": 1.2025, "volume": 2200}
    ]
    
    mock_indicators = {
        "RSI": {"rsi": [45, 50, 55, 60]},
        "MACD": {"macd": [0.001, 0.002, 0.003, 0.004], "signal": [0.001, 0.0015, 0.002, 0.0025]}
    }
    
    market_data = {"candles": mock_candles}
    
    # Price Action Trigger
    print("🔄 Price Action Trigger:")
    pa_trigger = PriceActionTrigger({})
    pa_signal = pa_trigger.evaluate(market_data, mock_indicators)
    print(f"   Action: {pa_signal['action']}")
    print(f"   Confidence: {pa_signal['confidence']:.2f}")
    print(f"   Reason: {pa_signal['reason']}")
    
    # Volume Spike Trigger
    print("\n📊 Volume Spike Trigger:")
    vs_trigger = VolumeSpikeTrigger({"spike_threshold": 1.3})
    vs_signal = vs_trigger.evaluate(market_data, mock_indicators)
    print(f"   Action: {vs_signal['action']}")
    print(f"   Confidence: {vs_signal['confidence']:.2f}")
    print(f"   Reason: {vs_signal['reason']}")


async def demo_configuration():
    """Demonstrate configuration system."""
    print("\n⚙️ Configuration System Demo")
    print("=" * 50)
    
    from src.config.trading_config import config_parser
    
    # Load configuration
    config = config_parser.load_config()
    trading_config = config.trading
    
    print(f"📋 Trading Configuration:")
    print(f"   Max Daily Trades: {trading_config.max_daily_trades}")
    print(f"   Balance: {trading_config.balance}")
    print(f"   Wake Interval: {trading_config.wake_interval}")
    print(f"   Trade Amount Ratio: {trading_config.trade_amount_ratio}")
    print(f"   Win Multiplier: {trading_config.win_amount_multiplier}")
    print(f"   Timeframes: {', '.join(trading_config.timeframes)}")
    print(f"   Context Feeds: {', '.join(trading_config.context_feeds) if trading_config.context_feeds else 'None configured'}")
    print(f"   Triggers: {', '.join(trading_config.triggers) if trading_config.triggers else 'None configured'}")
    
    if trading_config.trading_hours:
        print(f"   Trading Hours: {trading_config.trading_hours.start} - {trading_config.trading_hours.end}")
    
    if trading_config.trading_sessions:
        print(f"   Trading Sessions: {', '.join(trading_config.trading_sessions)}")


async def demo_manifest_loading():
    """Demonstrate custom manifest loading."""
    print("\n📦 Manifest System Demo")
    print("=" * 50)
    
    from src.core.manifests import manifest_loader
    
    # Check if custom manifests exist
    custom_files = [
        "custom_indicators/CustomIndicator.yml",
        "triggers/CustomTrigger.yml", 
        "news/NewsSentimentFeed.yml"
    ]
    
    print("📂 Available Custom Manifests:")
    for file_path in custom_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            # Try to load the manifest
            manifest = manifest_loader.load_manifest_from_file(file_path)
            if manifest:
                print(f"      📋 {manifest.name} v{manifest.version}")
                print(f"      📝 {manifest.description}")
        else:
            print(f"   ❌ {file_path} (not found)")


async def main():
    """Run the comprehensive demo."""
    print("🚀 IQ Option Bot API - New Features Demo")
    print("=" * 60)
    
    demos = [
        demo_configuration(),
        demo_chart_data(),
        demo_indicators(),
        demo_triggers(),
        demo_manifest_loading(),
    ]
    
    for demo in demos:
        try:
            await demo
            await asyncio.sleep(0.5)  # Small pause between demos
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    print("\n🎉 Demo completed successfully!")
    print("\nTo start the trading agent:")
    print("  from src.core.trading_agent import TradingAgent")  
    print("  agent = TradingAgent()")
    print("  await agent.start()")
    print("\nOr use the REST API:")
    print("  POST /api/v1/chart/agent/start")


if __name__ == "__main__":
    asyncio.run(main())