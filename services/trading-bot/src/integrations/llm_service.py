"""
LLM Service Client for Trading Bot
This client connects the trading bot to the LLM Gateway service.
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class LLMServiceClient:
    """Client for connecting to the LLM Gateway service"""
    
    def __init__(self, base_url: str = "http://llm-gateway:8001"):
        self.base_url = base_url
        
    async def health_check(self) -> Dict[str, Any]:
        """Check if LLM Gateway is healthy"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
    
    async def list_providers(self) -> Dict[str, Any]:
        """Get available LLM providers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/providers")
            response.raise_for_status()
            return response.json()
    
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Get completion from LLM Gateway"""
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if provider:
            payload["provider"] = provider
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/completion",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    async def get_trading_analysis(
        self,
        market_data: Dict[str, Any],
        asset: str = "EURUSD"
    ) -> Dict[str, Any]:
        """Get AI-powered trading analysis"""
        
        # Create trading analysis prompt
        prompt = f"""You are an expert binary options trader analyzing {asset}.

Market Data:
- Current Price: {market_data.get('price', 'N/A')}
- Timestamp: {market_data.get('timestamp', 'N/A')}
- Volume: {market_data.get('volume', 'N/A')}

Based on this data, provide a trading recommendation:
1. Direction: CALL or PUT
2. Confidence: 1-10 scale
3. Reasoning: Brief explanation (max 50 words)

Respond in this format:
DIRECTION: [CALL/PUT]
CONFIDENCE: [1-10]
REASONING: [Your brief analysis]"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = await self.get_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent trading advice
                max_tokens=150
            )
            
            # Parse the result
            content = result.get('content', '')
            
            analysis = {
                'direction': 'CALL',  # Default
                'confidence': 5,      # Default
                'reasoning': content[:100],  # Truncate
                'raw_response': content
            }
            
            # Try to parse structured response
            lines = content.split('\n')
            for line in lines:
                if 'DIRECTION:' in line:
                    direction = line.split(':')[1].strip()
                    if direction in ['CALL', 'PUT']:
                        analysis['direction'] = direction
                elif 'CONFIDENCE:' in line:
                    try:
                        confidence = int(line.split(':')[1].strip().split()[0])
                        if 1 <= confidence <= 10:
                            analysis['confidence'] = confidence
                    except:
                        pass
                elif 'REASONING:' in line:
                    reasoning = line.split(':', 1)[1].strip()
                    analysis['reasoning'] = reasoning
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting trading analysis: {e}")
            return {
                'direction': 'CALL',
                'confidence': 1,
                'reasoning': 'Analysis failed - using default recommendation',
                'error': str(e)
            }


# Singleton instance for the trading bot
llm_client = LLMServiceClient()