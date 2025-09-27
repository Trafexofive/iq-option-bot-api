#
# services/llm_gateway/providers/gemini_provider.py
#
import os
import google.generativeai as genai
from google.api_core import exceptions
from provider_base import LLMProvider, CompletionRequest, CompletionResponse

class GeminiProvider(LLMProvider):
    def __init__(self):
        self._api_key = os.environ.get("GEMINI_API_KEY")
        self._model = None

    def get_name(self) -> str:
        return "gemini"

    async def _lazy_init(self):
        if self._model:
            return
        if not self._api_key:
            raise ValueError("Gemini API key is not configured.")
        try:
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            raise RuntimeError(f"Failed to configure Gemini client: {e}")

    async def is_available(self) -> bool:
        return bool(self._api_key)

    async def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        await self._lazy_init()
        if not self._model:
            raise RuntimeError("Gemini model is not initialized.")
        
        gemini_messages = [{"role": "user", "parts": [msg.content]} for msg in request.messages]
        
        try:
            response = await self._model.generate_content_async(
                gemini_messages,
                stream=False
            )
            return CompletionResponse(
                content=response.text,
                provider_name=self.get_name(),
                model='gemini-1.5-flash'
            )
        except exceptions.ResourceExhausted as e:
            # Re-raise with a more specific HTTP exception context if needed at the gateway level
            raise RuntimeError(f"Gemini API rate limit exceeded: {e}")


    async def get_streaming_completion(self, request: CompletionRequest):
        await self._lazy_init()
        if not self._model:
            raise RuntimeError("Gemini model is not initialized.")
        
        gemini_messages = [{"role": "user", "parts": [msg.content]} for msg in request.messages]
        
        try:
            response = await self._model.generate_content_async(
                gemini_messages,
                stream=True
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except exceptions.ResourceExhausted as e:
            yield f"Error: Gemini API rate limit exceeded. {e}"
