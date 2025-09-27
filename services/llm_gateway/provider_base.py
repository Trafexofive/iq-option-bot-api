# ======================================================================================
# Provider Base - Final Version
#
# Description:
# Defines the core interfaces for all providers. The `CompletionResponse` model is
# updated to accept floats in its `usage` dictionary to correctly parse responses
# from providers like Groq that return fractional time values.
# ======================================================================================
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class CompletionRequest(BaseModel):
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

class CompletionResponse(BaseModel):
    content: str
    provider_name: str
    model: str
    usage: Dict[str, int | float] = {}

class LLMProvider(ABC):
    @abstractmethod
    async def get_completion(self, request: CompletionRequest) -> CompletionResponse:
        pass

    @abstractmethod
    async def get_streaming_completion(self, request: CompletionRequest):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

