#
# services/llm_gateway/providers/ollama_provider.py
#
import os
import httpx
import json
import logging
from provider_base import LLMProvider, CompletionRequest, CompletionResponse

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model_name = os.environ.get("OLLAMA_DEFAULT_MODEL", "llama3")
        self._endpoint = None
        self._legacy_format = False

    def get_name(self) -> str:
        return "ollama"

    async def _probe_endpoint(self):
        if self._endpoint is not None:
            return
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(f"{self.base_url}/api/chat", follow_redirects=True)
                if response.status_code == 404:
                    logger.warning("Ollama endpoint /api/chat not found. Falling back to legacy /api/generate.")
                    self._endpoint = "/api/generate"
                    self._legacy_format = True
                else:
                    logger.info("Confirmed modern Ollama endpoint at /api/chat (status: %d).", response.status_code)
                    self._endpoint = "/api/chat"
                    self._legacy_format = False
        except httpx.RequestError as e:
            logger.warning("Could not connect to Ollama to probe endpoint: %s. Assuming legacy /api/generate.", e)
            self._endpoint = "/api/generate"
            self._legacy_format = True

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(self.base_url, timeout=3.0)
                if self._endpoint is None:
                    await self._probe_endpoint()
                return response.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def _prepare_payload(self, request: CompletionRequest, stream: bool) -> dict:
        """Correctly prepares the payload including all options."""
        if self._legacy_format:
            prompt = "\n".join([f"{msg.content}" for msg in request.messages])
            payload = {"model": self.model_name, "prompt": prompt, "stream": stream}
        else:
            payload = {"model": self.model_name, "messages": [msg.dict() for msg in request.messages], "stream": stream}
        
        options = {}
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if request.temperature is not None:
            options["temperature"] = request.temperature
        
        if options:
            payload["options"] = options
            
        return payload

    async def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        await self._probe_endpoint()
        payload = self._prepare_payload(request, stream=False)
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{self.base_url}{self._endpoint}", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("response") if self._legacy_format else data.get("message", {}).get("content", "")
            return CompletionResponse(content=content, provider_name=self.get_name(), model=data.get("model", self.model_name))

    async def get_streaming_completion(self, request: CompletionRequest):
        await self._probe_endpoint()
        payload = self._prepare_payload(request, stream=True)
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}{self._endpoint}", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    logger.info(f"Ollama raw stream line: {line}")
                    try:
                        data = json.loads(line)
                        chunk = data.get("response") if self._legacy_format else data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode JSON from line: {line}")
                        continue

