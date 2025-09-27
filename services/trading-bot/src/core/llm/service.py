import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from src.models.trading import LLMResponse, TradeDirection
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients
    """
    @abstractmethod
    async def get_completion(self, prompt: str) -> str:
        pass


class OpenAILLMClient(BaseLLMClient):
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is not set in settings")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def get_completion(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using a more cost-effective model
            messages=[
                {"role": "system", "content": "You are an expert trading assistant. Provide concise, actionable trading advice based on market data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent responses
        )
        return response.choices[0].message.content


class AnthropicLLMClient(BaseLLMClient):
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key is not set in settings")
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def get_completion(self, prompt: str) -> str:
        response = await self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.3,
            system="You are an expert trading assistant. Provide concise, actionable trading advice based on market data.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text


class OllamaLLMClient(BaseLLMClient):
    def __init__(self):
        import httpx
        self.base_url = settings.ollama_base_url
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def get_completion(self, prompt: str) -> str:
        response = await self.http_client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": "llama3.2",  # Using a lightweight model for local inference
                "prompt": f"System: You are an expert trading assistant. Provide concise, actionable trading advice based on market data.\n\nUser: {prompt}\n\nAssistant:",
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]


class GeminiLLMClient(BaseLLMClient):
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key is not set in settings")
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def get_completion(self, prompt: str) -> str:
        import google.generativeai as genai
        from google.generativeai.types import generation_types
        
        # Note: Gemini doesn't have a native async API, so we'll use a thread executor
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def sync_generate():
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                )
            )
            return response.text
            
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, sync_generate)
        return result


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        self.client = self._initialize_client()

    def _initialize_client(self) -> BaseLLMClient:
        if self.provider == "openai":
            return OpenAILLMClient()
        elif self.provider == "anthropic":
            return AnthropicLLMClient()
        elif self.provider == "ollama":
            return OllamaLLMClient()
        elif self.provider == "gemini":
            return GeminiLLMClient()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def get_trading_decision(
        self, 
        asset: str, 
        market_data: Dict[str, Any], 
        risk_level: float = 0.5
    ) -> LLMResponse:
        """
        Get trading decision from LLM based on market data
        """
        try:
            # Format the prompt for the LLM
            prompt = self._create_trading_prompt(asset, market_data, risk_level)
            
            # Get response from LLM
            llm_response = await self.client.get_completion(prompt)
            
            # Parse the response into a structured format
            return self._parse_llm_response(llm_response, market_data)
        except Exception as e:
            logger.error(f"Error getting trading decision from LLM: {str(e)}")
            raise

    def _create_trading_prompt(self, asset: str, market_data: Dict[str, Any], risk_level: float) -> str:
        """
        Create a prompt for the LLM with market data
        """
        prompt = f"""
        Analyze the following market data for {asset} and provide a trading recommendation:

        Market Data:
        - Current price: {market_data.get('price', 'N/A')}
        - Timestamp: {market_data.get('timestamp', 'N/A')}
        - Volume: {market_data.get('volume', 'N/A')}
        - Bid: {market_data.get('bid', 'N/A')}
        - Ask: {market_data.get('ask', 'N/A')}
        - Spread: {market_data.get('spread', 'N/A')}

        Risk Level: {risk_level} (0.0 = very low risk, 1.0 = very high risk)

        Please provide your analysis in the following format:
        1. Decision: CALL or PUT
        2. Confidence: 0.0 to 1.0
        3. Reasoning: Brief explanation
        4. Entry Price: Suggested entry price
        5. Stop Loss: Optional stop loss price
        6. Take Profit: Optional take profit price
        7. Time Frame: Duration for the trade (e.g., "1m", "5m", "15m")

        Keep your response concise and focused on actionable trading advice.
        """
        return prompt

    def _parse_llm_response(self, llm_response: str, market_data: Dict[str, Any]) -> LLMResponse:
        """
        Parse the LLM response into a structured LLMResponse object
        This is a simplified implementation - in production, you might want to use 
        more sophisticated parsing like JSON format from the LLM or regex patterns.
        """
        # For now, return a mock response to demonstrate the structure
        # In a real implementation, you'd parse the actual LLM response
        
        # For demonstration purposes, we'll return a mock response
        # A real implementation would involve processing the llm_response string
        # to extract the required fields
        
        import re
        
        # Mock parsing based on expected format from the prompt
        # This would need to be more robust in a production system
        decision = TradeDirection.CALL  # Default value
        confidence = 0.6  # Default value
        reasoning = llm_response[:100]  # First 100 chars as reasoning
        entry_price = market_data.get('price', 0.0)  # Use current market price as entry
        stop_loss = None
        take_profit = None
        time_frame = "5m"  # Default time frame
        
        # Try to extract values from the response (simplified regex approach)
        if "Decision: PUT" in llm_response:
            decision = TradeDirection.PUT
        
        confidence_match = re.search(r"Confidence: ([0-9.]+)", llm_response)
        if confidence_match:
            confidence = float(confidence_match.group(1))
        
        reasoning_match = re.search(r"Reasoning: (.+?)(?=\n|$)", llm_response)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        entry_match = re.search(r"Entry Price: ([0-9.]+)", llm_response)
        if entry_match:
            entry_price = float(entry_match.group(1))
        
        stop_match = re.search(r"Stop Loss: ([0-9.]+)", llm_response)
        if stop_match:
            stop_loss = float(stop_match.group(1))
        
        profit_match = re.search(r"Take Profit: ([0-9.]+)", llm_response)
        if profit_match:
            take_profit = float(profit_match.group(1))
            
        time_match = re.search(r"Time Frame: ([0-9]+[mhd])", llm_response)
        if time_match:
            time_frame = time_match.group(1)

        return LLMResponse(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            time_frame=time_frame
        )

    async def get_available_providers(self) -> list:
        """
        Get list of available LLM providers
        """
        return ["openai", "anthropic", "ollama", "gemini"]