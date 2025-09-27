"""
Trading Bot to LLM Gateway Integration
This module connects the trading bot service to the LLM Gateway
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TradingLLMIntegration:
    """Integration layer between trading bot and LLM Gateway"""
    
    def __init__(self, llm_gateway_url: str = "http://llm-gateway:8001"):
        self.llm_gateway_url = llm_gateway_url
        self.timeout = httpx.Timeout(30.0)
    
    async def get_trading_recommendation(
        self,
        asset: str,
        market_data: Dict[str, Any],
        provider: str = "gemini"
    ) -> Dict[str, Any]:
        """
        Get AI-powered trading recommendation
        
        Args:
            asset: Trading pair (e.g. "EURUSD")
            market_data: Current market data
            provider: LLM provider to use
            
        Returns:
            Dict with recommendation details
        """
        
        # Create structured prompt for trading analysis
        prompt = f"""Analyze {asset} for binary options trading:

Market Data:
- Price: {market_data.get('price', 'N/A')}
- Volume: {market_data.get('volume', 'N/A')}
- Timestamp: {market_data.get('timestamp', 'N/A')}

Provide a trading recommendation in this exact format:
DIRECTION: [CALL or PUT]
CONFIDENCE: [1-10]
REASONING: [Brief explanation in max 30 words]

Be concise and decisive."""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.llm_gateway_url}/completion",
                    json={
                        "provider": provider,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._parse_trading_recommendation(result.get('content', ''))
                else:
                    logger.error(f"LLM Gateway error: {response.status_code}")
                    return self._default_recommendation()
                    
        except Exception as e:
            logger.error(f"Trading recommendation failed: {e}")
            return self._default_recommendation()
    
    def _parse_trading_recommendation(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured recommendation"""
        
        recommendation = {
            'direction': 'CALL',  # Default
            'confidence': 5,      # Default
            'reasoning': 'Analysis unavailable',
            'raw_response': content
        }
        
        try:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if 'DIRECTION:' in line:
                    direction = line.split(':')[1].strip()
                    if direction.upper() in ['CALL', 'PUT']:
                        recommendation['direction'] = direction.upper()
                        
                elif 'CONFIDENCE:' in line:
                    try:
                        conf_str = line.split(':')[1].strip()
                        confidence = int(conf_str.split()[0])  # Get just the number
                        if 1 <= confidence <= 10:
                            recommendation['confidence'] = confidence
                    except:
                        pass
                        
                elif 'REASONING:' in line:
                    reasoning = line.split(':', 1)[1].strip()
                    if reasoning:
                        recommendation['reasoning'] = reasoning
                        
        except Exception as e:
            logger.warning(f"Error parsing recommendation: {e}")
        
        return recommendation
    
    def _default_recommendation(self) -> Dict[str, Any]:
        """Fallback recommendation when LLM fails"""
        return {
            'direction': 'CALL',
            'confidence': 1,
            'reasoning': 'LLM service unavailable - using conservative default',
            'fallback': True
        }
    
    async def health_check(self) -> bool:
        """Check if LLM Gateway is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.llm_gateway_url}/health")
                return response.status_code == 200
        except:
            return False


# Global integration instance
trading_llm = TradingLLMIntegration()