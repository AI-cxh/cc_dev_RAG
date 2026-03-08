"""Schemas for configuration operations"""

from typing import Literal
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration"""

    vendor: Literal["openai", "vllm", "ollama"]
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class EmbeddingConfig(BaseModel):
    """Embedding configuration"""

    vendor: Literal["openai", "local"]
    model: str
    dimension: int
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class RerankerConfig(BaseModel):
    """Reranker configuration"""

    enabled: bool
    model: str
    top_k: int = 10


class RagConfig(BaseModel):
    """RAG configuration"""

    chunk_size: int = 500
    chunk_overlap: float = 0.1
    max_retrieval_results: int = 20
    top_k_results: int = 5


class AgentConfig(BaseModel):
    """Agent configuration"""

    web_search_keywords: list[str]
    rewrite_threshold: float = 0.6
    max_rewrite_attempts: int = 2


class SettingsResponse(BaseModel):
    """Response for current settings"""

    llm: LLMConfig
    embedding: EmbeddingConfig
    reranker: RerankerConfig
    rag: RagConfig
    agent: AgentConfig


class SettingsUpdate(BaseModel):
    """Schema for updating settings"""

    llm: Optional[LLMConfig] = None
    embedding: Optional[EmbeddingConfig] = None
    reranker: Optional[RerankerConfig] = None
    rag: Optional[RagConfig] = None
    agent: Optional[AgentConfig] = None


class ModelInfo(BaseModel):
    """Schema for model information"""

    id: str
    name: str
    vendor: str
    type: Literal["llm", "embedding", "reranker"]
    is_local: bool
    description: str


class ModelsResponse(BaseModel):
    """Response for available models"""

    llm_models: list[ModelInfo]
    embedding_models: list[ModelInfo]
    reranker_models: list[ModelInfo]
