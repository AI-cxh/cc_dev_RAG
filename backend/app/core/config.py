"""Application configuration management"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # VLLM
    vllm_base_url: str = Field(default="http://localhost:8000/v1", alias="VLLM_BASE_URL")
    vllm_model: str = Field(default="vllm-model-name", alias="VLLM_MODEL")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

    # Embedding
    embedding_model_vendor: Literal["openai", "local"] = Field(
        default="openai", alias="EMBEDDING_MODEL_VENDOR"
    )
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")

    # Reranker
    reranker_enabled: bool = Field(default=True, alias="RERANKER_ENABLED")
    reranker_model: str = Field(default="bge-reranker-v2-m3", alias="RERANKER_MODEL")
    reranker_top_k: int = Field(default=10, alias="RERANKER_TOP_K")

    # Milvus
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_token: str = Field(default="root:Milvus", alias="MILVUS_TOKEN")

    # Database
    database_url: str = Field(default="sqlite:///./data/dialogues.db", alias="DATABASE_URL")

    # Application
    app_name: str = Field(default="RAG Agent Assistant", alias="APP_NAME")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="DEBUG")

    # RAG Configuration
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: float = Field(default=0.1, alias="CHUNK_OVERLAP")
    max_retrieval_results: int = Field(default=20, alias="MAX_RETRIEVAL_RESULTS")
    top_k_results: int = Field(default=5, alias="TOP_K_RESULTS")

    # Query Routing
    web_search_keywords: str = Field(
        default="搜索,最新,实时,今天,本周,本月,新闻",
        alias="WEB_SEARCH_KEYWORDS",
    )
    rewrite_threshold: float = Field(default=0.6, alias="REWRITE_THRESHOLD")
    max_rewrite_attempts: int = Field(default=2, alias="MAX_REWRITE_ATTEMPTS")

    # Frontend
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    @property
    def web_search_keywords_list(self) -> list[str]:
        """Parse web search keywords into a list"""
        return [k.strip() for k in self.web_search_keywords.split(",") if k.strip()]

    @property
    def is_llm_configured(self) -> bool:
        """Check if any LLM is configured"""
        return bool(self.openai_api_key or self.vllm_model or self.ollama_model)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
