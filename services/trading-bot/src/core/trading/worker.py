"""
Background worker for the LLM trading bot
Handles tasks like:
- Monitoring open trades
- Executing scheduled strategies
- Processing market data
"""
import asyncio
import logging
from config.settings import settings
from src.core.market.service import MarketService
from src.core.trading.service import TradingService
from src.core.llm.service import LLMService

# Set up logging
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting LLM Trading Bot Worker...")
    
    # Initialize services
    market_service = MarketService()
    trading_service = TradingService()
    llm_service = LLMService()
    
    # Startup services
    await market_service.startup()
    
    try:
        # Main worker loop
        while True:
            logger.debug("Worker running...")
            # Add your background tasks here
            
            # Example: periodically check market data
            # market_data = await market_service.get_market_data("EURUSD")
            # logger.info(f"Current EURUSD price: {market_data.price}")
            
            await asyncio.sleep(30)  # Run every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
    finally:
        # Shutdown services
        await market_service.shutdown()
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())