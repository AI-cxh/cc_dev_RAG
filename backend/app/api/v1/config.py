"""Configuration API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Literal

from app.core.config import settings
from app.schemas import SettingsResponse, ModelsResponse, ModelInfo, SettingsUpdate
from pydantic import BaseModel

router = APIRouter()


class LLMConfigResponse(BaseModel):
    vendor: Literal["openai", "vllm", "ollama"]
    model: str
    api_configured: bool


class EmbeddingConfigResponse(BaseModel):
    vendor: Literal["openai", "local"]
    model: str
    dimension: int


class ConfigResponse(BaseModel):
    llm: LLMConfigResponse
    embedding: EmbeddingConfigResponse
    reranker_enabled: bool
    reranker_model: str
    tavily_configured: bool


@router.get("/settings", response_model=ConfigResponse)
async def get_settings():
    """Get current configuration"""
    llm_vendor = "openai"
    llm_model = settings.openai_model
    api_configured = bool(settings.openai_api_key)

    # Determine active LLM vendor based on configuration
    if settings.openai_api_key:
        llm_vendor = "openai"
        llm_model = settings.openai_model
        api_configured = True
    elif settings.ollama_base_url:
        llm_vendor = "ollama"
        llm_model = settings.ollama_model
        api_configured = True

    return ConfigResponse(
        llm=LLMConfigResponse(
            vendor=llm_vendor,
            model=llm_model,
            api_configured=api_configured,
        ),
        embedding=EmbeddingConfigResponse(
            vendor=settings.embedding_model_vendor,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        ),
        reranker_enabled=settings.reranker_enabled,
        reranker_model=settings.reranker_model,
        tavily_configured=bool(settings.tavily_api_key),
    )


# Available models registry
AVAILABLE_MODELS: dict[str, dict] = {
    "llm": [
        {
            "id": "openai:gpt-4o-mini",
            "name": "GPT-4o Mini",
            "vendor": "openai",
            "type": "llm",
            "is_local": False,
            "description": "OpenAI GPT-4o Mini - fast and cost-effective",
        },
        {
            "id": "openai:gpt-4o",
            "name": "GPT-4o",
            "vendor": "openai",
            "type": "llm",
            "is_local": False,
            "description": "OpenAI GPT-4o - powerful multimodal model",
        },
        {
            "id": "ollama:llama3",
            "name": "Llama 3 (Ollama)",
            "vendor": "ollama",
            "type": "llm",
            "is_local": True,
            "description": "Meta Llama 3 via Ollama",
        },
        {
            "id": "ollama:mistral",
            "name": "Mistral (Ollama)",
            "vendor": "ollama",
            "type": "llm",
            "is_local": True,
            "description": "Mistral AI model via Ollama",
        },
        {
            "id": "vllm:custom-model",
            "name": "Custom VLLM Model",
            "vendor": "vllm",
            "type": "llm",
            "is_local": True,
            "description": "Custom model via VLLM",
        },
    ],
    "embedding": [
        {
            "id": "openai:text-embedding-3-small",
            "name": "Text Embedding 3 Small",
            "vendor": "openai",
            "type": "embedding",
            "is_local": False,
            "description": "OpenAI text-embedding-3-small - 1536 dimensions",
        },
        {
            "id": "openai:text-embedding-3-large",
            "name": "Text Embedding 3 Large",
            "vendor": "openai",
            "type": "embedding",
            "is_local": False,
            "description": "OpenAI text-embedding-3-large - 3072 dimensions",
        },
        {
            "id": "local:bge-m3",
            "name": "BGE-M3",
            "vendor": "local",
            "type": "embedding",
            "is_local": True,
            "description": "BGE-M3 multilingual embedding model - 1024 dimensions",
        },
        {
            "id": "local:bge-small-zh",
            "name": "BGE-Small-ZH",
            "vendor": "local",
            "type": "embedding",
            "is_local": True,
            "description": "BGE-Small Chinese - 512 dimensions",
        },
    ],
    "reranker": [
        {
            "id": "reranker:bge-reranker-v2-m3",
            "name": "BGE Reranker v2 M3",
            "vendor": "local",
            "type": "reranker",
            "is_local": True,
            "description": "BGE Reranker v2 M3 for multilingual",
        },
        {
            "id": "reranker:bge-reranker-large",
            "name": "BGE Reranker Large",
            "vendor": "local",
            "type": "reranker",
            "is_local": True,
            "description": "BGE Reranker Large",
        },
        {
            "id": "reranker:cohere-rerank",
            "name": "Cohere Rerank API",
            "vendor": "cohere",
            "type": "reranker",
            "is_local": False,
            "description": "Cohere Rerank API",
        },
    ],
}


@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """Get available models configuration"""
    return ModelsResponse(
        llm_models=[ModelInfo(**m) for m in AVAILABLE_MODELS["llm"]],
        embedding_models=[ModelInfo(**m) for m in AVAILABLE_MODELS["embedding"]],
        reranker_models=[ModelInfo(**m) for m in AVAILABLE_MODELS["reranker"]],
    )


@router.get("/llm-models")
async def get_llm_models():
    """Get available LLM models"""
    return AVAILABLE_MODELS["llm"]


@router.get("/embedding-models")
async def get_embedding_models():
    """Get available Embedding models"""
    return AVAILABLE_MODELS["embedding"]


@router.get("/reranker-models")
async def get_reranker_models():
    """Get available Reranker models"""
    return AVAILABLE_MODELS["reranker"]
