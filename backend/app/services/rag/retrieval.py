"""Retrieval service and knowledge base management"""

import time
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from pymilvus import Collection, connections, utility
from langchain_core.documents import Document

from app.core.config import settings
from app.services.llm.embeddings import get_embedding_service, get_milvus_embedding_function
from app.services.llm.rerankers import get_reranker


class KnowledgeBaseService:
    """Service for managing knowledge bases"""

    def __init__(self):
        """Initialize Milvus connection"""
        self._connect_milvus()
        self._kbs: Dict[int, Dict] = {}
        self._kb_id_counter = 0

    def _connect_milvus(self):
        """Connect to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port,
                token=settings.milvus_token,
            )
            print(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")
        except Exception as e:
            print(f"Warning: Failed to connect to Milvus: {e}")

    def create_knowledge_base(
        self,
        name: str,
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new knowledge base"""
        self._kb_id_counter += 1
        kb_id = self._kb_id_counter

        kb_data = {
            "id": kb_id,
            "name": name,
            "description": description,
            "document_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        self._kbs[kb_id] = kb_data

        # Create Milvus collection for this KB
        self._create_collection(kb_id)

        return kb_data

    def _create_collection(self, kb_id: int):
        """Create Milvus collection for a knowledge base"""
        collection_name = f"kb_{kb_id}"

        # Check if collection already exists
        if utility.has_collection(collection_name):
            return

        from pymilvus import FieldSchema, CollectionSchema, DataType

        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.embedding_dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="kb_id", dtype=DataType.INT64),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=36),
            FieldSchema(name="doc_name", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="page_num", dtype=DataType.INT64),
        ]

        schema = CollectionSchema(fields=fields, description=f"Knowledge base {kb_id}")

        # Create collection
        collection = Collection(
            name=collection_name,
            schema=schema,
        )

        # Create index on embedding
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()

        print(f"Created Milvus collection: {collection_name}")

    def delete_knowledge_base(self, kb_id: int) -> bool:
        """Delete a knowledge base"""
        if kb_id not in self._kbs:
            return False

        # Drop Milvus collection
        collection_name = f"kb_{kb_id}"
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)

        del self._kbs[kb_id]
        return True

    def list_knowledge_bases(self) -> List[Dict]:
        """List all knowledge bases"""
        return list(self._kbs.values())

    def get_knowledge_base(self, kb_id: int) -> Optional[Dict]:
        """Get knowledge base by ID"""
        return self._kbs.get(kb_id)

    def add_document(
        self,
        kb_id: int,
        doc_id: str,
        doc_name: str,
        chunks: List[Dict],
    ) -> Dict:
        """Add a document to a knowledge base"""
        if kb_id not in self._kbs:
            raise ValueError(f"Knowledge base {kb_id} not found")

        collection = Collection(f"kb_{kb_id}")

        # Prepare data for insertion
        ids = [str(uuid.uuid4()) for _ in chunks]
        embeddings = []
        contents = []
        kb_ids = []
        doc_ids = []
        doc_names = []
        chunk_indices = []
        page_nums = []

        embedding_service = get_embedding_service()

        for chunk in chunks:
            content = chunk["content"]
            metadata = chunk.get("metadata", {})

            # Get or generate embedding
            if "embedding" in metadata:
                embeddings.append(metadata["embedding"])
            else:
                embedding = embedding_service.embed_query(content)
                embeddings.append(embedding)

            contents.append(content)
            kb_ids.append(kb_id)
            doc_ids.append(doc_id)
            doc_names.append(doc_name)
            chunk_indices.append(metadata.get("chunk_index", 0))
            page_nums.append(metadata.get("page_num", -1))

        # Insert into Milvus
        data = [
            ids,
            embeddings,
            contents,
            kb_ids,
            doc_ids,
            doc_names,
            chunk_indices,
            page_nums,
        ]

        insert_result = collection.insert(data)
        collection.flush()

        # Update KB metadata
        self._kbs[kb_id]["document_count"] += 1
        self._kbs[kb_id]["updated_at"] = datetime.utcnow()

        return {
            "doc_id": doc_id,
            "chunk_count": len(chunks),
            "insert_ids": insert_result.insert_ids,
        }

    def delete_document(self, kb_id: int, doc_id: str) -> bool:
        """Delete a document from a knowledge base"""
        if kb_id not in self._kbs:
            return False

        collection = Collection(f"kb_{kb_id}")

        # Delete all chunks for this doc_id
        # Note: This is a simplified approach - in production you'd want more sophisticated deletion
        result = collection.delete(f"doc_id == '{doc_id}'")
        collection.flush()

        # Update KB metadata
        self._kbs[kb_id]["document_count"] -= 1
        self._kbs[kb_id]["updated_at"] = datetime.utcnow()

        return True

    def get_document_count(self, kb_id: int) -> int:
        """Get number of documents in a knowledge base"""
        kb = self.get_knowledge_base(kb_id)
        return kb["document_count"] if kb else 0


class RetrievalService:
    """Service for retrieving documents from knowledge bases"""

    def __init__(
        self,
        top_k: int = 5,
        reranker_enabled: bool = True,
    ):
        """
        Initialize retrieval service

        Args:
            top_k: Number of documents to retrieve
            reranker_enabled: Whether to use reranking
        """
        self.top_k = top_k
        self.reranker_enabled = reranker_enabled
        self.embedding_service = get_embedding_service()
        self.reranker = get_reranker() if reranker_enabled else None

    def retrieve(
        self,
        query: str,
        kb_id: int,
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        Retrieve documents from a knowledge base

        Args:
            query: Search query
            kb_id: Knowledge base ID
            top_k: Number of documents to retrieve

        Returns:
            List of Document objects
        """
        top_k = top_k or self.top_k

        # Get query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Search in Milvus
        collection = Collection(f"kb_{kb_id}")
        collection.load()

        # Set search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10},
        }

        # Limit retrieval candidates
        retrieval_results = settings.max_retrieval_results

        # Search with Milvus's default top k
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=max(top_k, retrieval_results),
            output_fields=["content", "doc_id", "doc_name", "chunk_index", "page_num"],
        )

        # Convert results to Document objects
        documents = []
        for result in results[0]:
            doc = Document(
                page_content=result.entity.get("content"),
                metadata={
                    "score": result.score,
                    "doc_id": result.entity.get("doc_id"),
                    "doc_name": result.entity.get("doc_name"),
                    "chunk_index": result.entity.get("chunk_index"),
                    "page_num": result.entity.get("page_num"),
                },
            )
            documents.append(doc)

        # Rerank if enabled
        if self.reranker and self.reranker_enabled and len(documents) > top_k:
            documents = self.reranker.rerank(query, documents, top_k=top_k)

        return documents[:top_k]

    async def aretrieve(
        self,
        query: str,
        kb_id: int,
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """Asynchronously retrieve documents"""
        return self.retrieve(query, kb_id, top_k)
