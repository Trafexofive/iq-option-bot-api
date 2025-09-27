import logging
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from src.models.trading import TradeRequest, TradeResponse, TradeStatus, LLMResponse, TradeDirection
from src.integrations.iq_option.service import IQOptionService
from config.settings import settings

logger = logging.getLogger(__name__)


class TradingService:
    def __init__(self):
        self.iq_option_service = IQOptionService()
        self.risk_manager = RiskManager()

    async def execute_trade(
        self, 
        trade_request: TradeRequest, 
        llm_decision: LLMResponse
    ) -> TradeResponse:
        """
        Execute a trade based on LLM decision and risk management
        """
        try:
            # Validate risk management
            if not await self.risk_manager.validate_trade(trade_request, llm_decision):
                raise Exception("Trade blocked by risk management")

            # Execute the trade with IQ Option
            trade_result = await self.iq_option_service.execute_trade(
                asset=trade_request.asset,
                direction=trade_request.direction,
                amount=trade_request.amount,
                duration=trade_request.duration
            )

            # Create trade response
            trade_response = TradeResponse(
                trade_id=str(uuid4()),
                asset=trade_request.asset,
                direction=trade_request.direction,
                amount=trade_request.amount,
                entry_price=llm_decision.entry_price,
                status=TradeStatus.EXECUTED if trade_result["success"] else TradeStatus.CANCELLED,
                profit=trade_result.get("profit"),
                created_at=datetime.utcnow()
            )

            # Log the trade
            logger.info(f"Executed trade: {trade_response.trade_id} for asset {trade_request.asset}")

            return trade_response
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            raise

    async def get_recent_trades(self) -> List[TradeResponse]:
        """
        Get recent trades from the IQ Option service
        """
        try:
            trades = await self.iq_option_service.get_recent_trades()
            return trades
        except Exception as e:
            logger.error(f"Error getting recent trades: {str(e)}")
            raise


class RiskManager:
    """
    Manages risk for trading decisions
    """
    def __init__(self):
        self.daily_pnl = 0.0
        self.daily_loss_limit = settings.max_daily_risk
        self.trade_risk_limit = settings.default_risk_per_trade

    async def validate_trade(self, trade_request: TradeRequest, llm_decision: LLMResponse) -> bool:
        """
        Validate if a trade should be executed based on risk management rules
        """
        # Check if daily loss limit is reached
        if self.daily_pnl <= -self.daily_loss_limit:
            logger.warning("Daily loss limit reached, blocking trade")
            return False

        # Check if trade size is within limits
        if trade_request.amount > self.trade_risk_limit:
            logger.warning(f"Trade amount {trade_request.amount} exceeds risk limit {self.trade_risk_limit}")
            return False

        # Additional risk checks can be added here
        # For example, check correlation with existing positions
        # Check volatility metrics, etc.
        
        return True