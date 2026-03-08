"""Base LLM service supporting multiple vendors"""

from functools import lru_cache
from typing import Optional, AsyncIterator

from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.core.config import settings


class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming responses"""

    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.tokens.append(token)

    def get_tokens(self) -> str:
        """Get all accumulated tokens"""
        return "".join(self.tokens)

    def reset(self) -> None:
        """Reset token buffer"""
        self.tokens = []


class LLMService:
    """LLM service base class"""

    def __init__(
        self,
        vendor: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
    ):
        self.vendor = vendor
        self.model = model or self._get_default_model(vendor)
        self.api_key = api_key
        self.base_url = base_url or self._get_base_url(vendor)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming

        self._llm = self._create_llm()

    def _get_default_model(self, vendor: str) -> str:
        """Get default model for vendor"""
        if vendor == "openai":
            return settings.openai_model
        elif vendor == "vllm":
            return settings.vllm_model
        elif vendor == "ollama":
            return settings.ollama_model
        return "unknown"

    def _get_base_url(self, vendor: str) -> Optional[str]:
        """Get base URL for vendor"""
        if vendor == "openai":
            return settings.openai_base_url
        elif vendor == "vllm":
            return settings.vllm_base_url
        elif vendor == "ollama":
            return settings.ollama_base_url
        return None

    def _create_llm(self) -> ChatOpenAI:
        """Create LLM instance"""
        if self.vendor == "ollama":
            # Use OpenAI-compatible interface for Ollama
            llm = ChatOpenAI(
                model=self.model,
                base_url=self.base_url,
                api_key="ollama",  # Ollama doesn't require a real API key
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
            )
        elif self.vendor == "vllm":
            # Use OpenAI-compatible interface for VLLM
            llm = ChatOpenAI(
                model=self.model,
                base_url=self.base_url,
                api_key="vllm",  # VLLM doesn't require a real API key
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
            )
        else:  # openai
            llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key or settings.openai_api_key,
                base_url=self.base_url,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
            )

        return llm

    async def ainvoke(self, messages: list[BaseMessage]) -> AIMessage:
        """Invoke LLM asynchronously"""
        response = await self._llm.ainvoke(messages)
        return response

    async def astream(self, messages: list[BaseMessage]) -> AsyncIterator[str]:
        """Stream LLM response asynchronously"""
        async for chunk in self._llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    def invoke(self, messages: list[BaseMessage]) -> AIMessage:
        """Invoke LLM synchronously"""
        response = self._llm.invoke(messages)
        return response

    def stream(self, messages: list[BaseMessage]):
        """Stream LLM response synchronously"""
        for chunk in self._llm.stream(messages):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content


@lru_cache
def get_llm(
    vendor: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> LLMService:
    """Get cached LLM service instance"""
    return LLMService(
        vendor=vendor,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def create_messages_from(history: list[dict]) -> list[BaseMessage]:
    """Create LangChain messages from history dict"""
    messages = []

    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:  # user
            messages.append(HumanMessage(content=content))

    return messages
