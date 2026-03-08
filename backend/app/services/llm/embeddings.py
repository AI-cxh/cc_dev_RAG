"""Embedding service supporting multiple vendors"""

from functools import lru_cache
from typing import Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from pymilvus import AnnSearchBuilder
from pymilvus.model.dense import OpenAIEmbeddingFunction

from app.core.config import settings


class EmbeddingService:
    """Embedding service for generating text embeddings"""

    def __init__(
        self,
        vendor: str = "openai",
        model: Optional[str] = None,
        dimension: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        self.vendor = vendor
        self.model = model or settings.embedding_model
        self.dimension = dimension or settings.embedding_dimension
        self.api_key = api_key

        self._embedding = self._create_embedding()

    def _create_embedding(self):
        """Create embedding instance based on vendor"""
        if self.vendor == "local":
            return HuggingFaceEmbeddings(
                model_name=self._get_local_model_path(),
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:  # openai or openai compatible
            return OpenAIEmbeddings(
                model=self.model,
                api_key=self.api_key or settings.openai_api_key,
                base_url=settings.openai_base_url if self.vendor != "openai" else None,
            )

    def _get_local_model_path(self) -> str:
        """Get path for local model"""
        model_map = {
            "bge-m3": "BAAI/bge-m3",
            "bge-small-zh": "BAAI/bge-small-zh-v1.5",
            "bge-base-en": "BAAI/bge-base-en-v1.5",
            "bge-large-en": "BAAI/bge-large-en-v1.5",
        }
        return model_map.get(self.model, "BAAI/bge-small-zh-v1.5")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents"""
        return self._embedding.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query"""
        return self._embedding.embed_query(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts (alias for embed_documents)"""
        return self.embed_documents(texts)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents asynchronously"""
        return await self._embedding.aembed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        """Embed a single query asynchronously"""
        return await self._embedding.aembed_query(text)


@lru_cache
def get_embedding_service(
    vendor: Optional[str] = None,
    model: Optional[str] = None,
    dimension: Optional[int] = None,
    api_key: Optional[str] = None,
) -> EmbeddingService:
    """Get cached embedding service instance"""
    return EmbeddingService(
        vendor=vendor or settings.embedding_model_vendor,
        model=model or settings.embedding_model,
        dimension=dimension or settings.embedding_dimension,
        api_key=api_key,
    )


def get_milvus_embedding_function(
    vendor: str = "openai",
    model: Optional[str] = None,
    dimension: Optional[int] = None,
    api_key: Optional[str] = None,
):
    """Get Milvus embedding function"""
    if vendor == "openai" or vendor == "openai-compatible":
        return OpenAIEmbeddingFunction(
            model_name=model or settings.embedding_model,
            api_key=api_key or settings.openai_api_key,
        )

    # For local embeddings, we'll need to create a custom function
    from pymilvus.model.dense import BaseEmbeddingFunction

    class LocalEmbeddingFunction(BaseEmbeddingFunction):
        """Custom embedding function for local models"""

        def __init__(self, embedding_service: EmbeddingService):
            self.embedding_service = embedding_service

        def __call__(self, texts: str | list[str]) -> list[float] | list[list[float]]:
            if isinstance(texts, str):
                return self.embedding_service.embed_query(texts)
            return self.embedding_service.embed_documents(texts)

    embedding_service = EmbeddingService(vendor=vendor, model=model, dimension=dimension)
    return LocalEmbeddingFunction(embedding_service)
