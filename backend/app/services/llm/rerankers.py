"""Reranker service for improving retrieval results"""

from functools import lru_cache
from typing import Optional, list as list_type

from langchain_core.documents import Document

from app.services.llm.embeddings import get_embedding_service
from app.core.config import settings


class RerankerService:
    """Reranker service for improving retrieval results"""

    def __init__(
        self,
        model: str = "bge-reranker-v2-m3",
        top_k: int = 10,
    ):
        self.model = model
        self.top_k = top_k
        self._reranker = None
        self._load_reranker()

    def _load_reranker(self):
        """Load the reranker model"""
        try:
            from FlagEmbedding import FlagReranker

            self._reranker = FlagReranker(
                f"BAAI/{self.model}",
                use_fp16=True,
                device="cpu",  # Use CPU for MVP
            )
        except ImportError:
            # Fallback to simple similarity-based reranking
            self._reranker = None
            print(
                f"Warning: FlagEmbedding not installed, falling back to embedding-based reranking"
            )

    async def rerank(
        self,
        query: str,
        documents: list_type[Document],
        top_k: Optional[int] = None,
    ) -> list_type[Document]:
        """Rerank documents based on query relevance"""
        top_k = top_k or self.top_k

        if self._reranker:
            return await self._rerank_with_model(query, documents, top_k)
        else:
            return await self._rerank_with_embeddings(query, documents, top_k)

    async def _rerank_with_model(
        self,
        query: str,
        documents: list_type[Document],
        top_k: int,
    ) -> list_type[Document]:
        """Rerank using BGE reranker model"""
        pairs = [[query, doc.page_content] for doc in documents]
        scores = self._reranker.compute_score(pairs)

        # Sort by score and return top k
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:top_k]]

    async def _rerank_with_embeddings(
        self,
        query: str,
        documents: list_type[Document],
        top_k: int,
    ) -> list_type[Document]:
        """Rerank using embedding similarity"""
        embedding_service = get_embedding_service()

        # Get query embedding
        query_embedding = embedding_service.embed_query(query)

        # Get document embeddings and calculate similarity
        doc_embeddings = embedding_service.embed_documents([doc.page_content for doc in documents])

        # Calculate cosine similarity (simplified)
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        similarities = cosine_similarity(
            np.array([query_embedding]),
            np.array(doc_embeddings),
        )[0]

        # Sort and return top k
        scored_docs = list(zip(documents, similarities))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:top_k]]


@lru_cache
def get_reranker(
    model: Optional[str] = None,
    top_k: Optional[int] = None,
) -> RerankerService:
    """Get cached reranker service instance"""
    return RerankerService(
        model=model or settings.reranker_model,
        top_k=top_k or settings.reranker_top_k,
    )
