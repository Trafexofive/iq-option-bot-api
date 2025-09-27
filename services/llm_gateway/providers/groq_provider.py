import os
import httpx
import json
from typing import Optional
from provider_base import LLMProvider, CompletionRequest, CompletionResponse

class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model_name = "llama3-8b-8192"

    def get_name(self) -> str:
        return "groq"

    async def is_available(self) -> bool:
        return bool(self._api_key)

    async def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        if not self._api_key:
            raise ValueError("Groq API key is not configured.")

        headers = {"Authorization": f"Bearer {self._api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # The usage field from Groq contains floats, which the updated model now handles.
            usage_data = data.get("usage", {})
            
            return CompletionResponse(
                content=data["choices"][0]["message"]["content"],
                provider_name=self.get_name(),
                model=self.model_name,
                usage=usage_data
            )

    async def get_streaming_completion(self, request: CompletionRequest):
        if not self._api_key:
            raise ValueError("Groq API key is not configured.")

        headers = {"Authorization": f"Bearer {self._api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if data["choices"][0]["delta"].get("content"):
                                yield data["choices"][0]["delta"]["content"]
                        except json.JSONDecodeError:
                            continue
