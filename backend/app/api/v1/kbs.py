"""Knowledge Base API endpoints"""

from typing import Optional
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
import httpx

from app.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    DocumentResponse,
    UploadDocumentResponse,
    UploadProgress,
)
from app.services.rag.retrieval import KnowledgeBaseService
from app.services.rag.document import DocumentParser, DocumentChunker
from app.core.config import settings

router = APIRouter()

# Global knowledge base service instance
kb_service = KnowledgeBaseService()


@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """List all knowledge bases"""
    kbs = kb_service.list_knowledge_bases()
    return [
        {
            "id": kb["id"],
            "name": kb["name"],
            "description": kb["description"],
            "document_count": kb["document_count"],
            "created_at": kb["created_at"].isoformat() if hasattr(kb["created_at"], "isoformat") else kb["created_at"],
            "updated_at": kb["updated_at"].isoformat() if hasattr(kb["updated_at"], "isoformat") else kb["updated_at"],
        }
        for kb in kbs
    ]


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb: KnowledgeBaseCreate):
    """Create a new knowledge base"""
    kb_data = kb_service.create_knowledge_base(
        name=kb.name,
        description=kb.description,
    )
    return {
        "id": kb_data["id"],
        "name": kb_data["name"],
        "description": kb_data["description"],
        "document_count": kb_data["document_count"],
        "created_at": kb_data["created_at"].isoformat(),
        "updated_at": kb_data["updated_at"].isoformat(),
    }


@router.get("/{kb_id}")
async def get_knowledge_base(kb_id: int):
    """Get knowledge base by ID"""
    kb = kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    return {
        "id": kb["id"],
        "name": kb["name"],
        "description": kb["description"],
        "document_count": kb["document_count"],
        "created_at": kb["created_at"].isoformat(),
        "updated_at": kb["updated_at"].isoformat(),
    }


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: int):
    """Delete a knowledge base"""
    success = kb_service.delete_knowledge_base(kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"message": "Knowledge base deleted successfully"}


# Document storage (in-memory for MVP)
_documents: dict[int, dict] = {}
_doc_id_counter = 0


@router.get("/{kb_id}/documents")
async def list_documents(kb_id: int, limit: int = 50, offset: int = 0):
    """List documents in a knowledge base"""
    kb = kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    docs = [doc for doc in _documents.values() if doc["kb_id"] == kb_id]
    return docs[offset : offset + limit]


@router.post("/{kb_id}/documents/upload", response_model=UploadDocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
):
    """Upload a document to a knowledge base"""
    global _doc_id_counter

    # Check KB exists
    kb = kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Check document limit
    doc_count = kb.get("document_count", 0)
    if doc_count >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents allowed per knowledge base")

    # Check file format
    if not DocumentParser.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {', '.join(DocumentParser.SUPPORTED_FORMATS)}",
        )

    # Save uploaded file temporarily
    doc_id = str(uuid.uuid4())
    _doc_id_counter += 1

    # Create temp file
    temp_dir = Path("data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / f"{doc_id}_{file.filename}"

    async with httpx.AsyncClient() as client:
        # Read file content
        content = await file.read()
        temp_file.write_bytes(content)

    # Process document in background
    import asyncio

    async def process_document():
        """Parse, chunk, and embed document"""
        try:
            # Update status to parsing
            _documents[_doc_id_counter]["status"] = "parsing"
            _documents[_doc_id_counter]["progress"] = {
                "stage": "parsing",
                "progress": 0.3,
                "message": f"Parsing {file.filename}...",
            }

            # Parse document
            from app.services.rag.document import DocumentParser, DocumentChunker

            text, parse_metadata = DocumentParser.parse(str(temp_file))

            # Update status to chunking
            _documents[_doc_id_counter]["progress"] = {
                "stage": "chunking",
                "progress": 0.5,
                "message": "Chunking document...",
            }

            # Chunk document
            chunker = DocumentChunker(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )

            chunks = chunker.split_text_with_page_numbers(
                text,
                metadata={
                    "kb_id": kb_id,
                    "doc_id": doc_id,
                    "doc_name": file.filename,
                },
            )

            # Update status to embedding
            _documents[_doc_id_counter]["progress"] = {
                "stage": "embedding",
                "progress": 0.7,
                "message": f"Embedding {len(chunks)} chunks...",
            }

            # Add to knowledge base
            kb_service.add_document(
                kb_id=kb_id,
                doc_id=doc_id,
                doc_name=file.filename,
                chunks=chunks,
            )

            # Update status to completed
            _documents[_doc_id_counter]["status"] = "completed"
            _documents[_doc_id_counter]["progress"] = {
                "stage": "completed",
                "progress": 1.0,
                "message": "Document processing complete",
            }
            _documents[_doc_id_counter]["metadata"] = {
                "total_chunks": len(chunks),
                "chunk_size": settings.chunk_size,
                "parse_time": parse_metadata.get("parse_time", 0),
                "file_type": parse_metadata.get("file_type", "unknown"),
                "file_size": temp_file.stat().st_size,
            }

        except Exception as e:
            _documents[_doc_id_counter]["status"] = "failed"
            _documents[_doc_id_counter]["progress"] = {
                "stage": "failed",
                "progress": 1.0,
                "message": f"Processing failed: {str(e)}",
            }
        finally:
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass

    # Create document record
    _documents[_doc_id_counter] = {
        "id": _doc_id_counter,
        "kb_id": kb_id,
        "doc_id": doc_id,
        "doc_name": file.filename or "unnamed",
        "file_type": Path(file.filename or "").suffix.lower(),
        "file_size": len(content),
        "status": "uploading",
        "progress": {
            "stage": "uploading",
            "progress": 0.1,
            "message": "Document uploaded, starting processing...",
        },
        "metadata": None,
        "created_at": "2024-01-01T00:00:00",
    }

    # Start background processing
    asyncio.create_task(process_document())

    return UploadDocumentResponse(
        document_id=_doc_id_counter,
        status="processing",
        progress=UploadProgress(
            stage="uploading",
            progress=0.1,
            message="Document uploaded, starting processing...",
        ),
    )


@router.delete("/{kb_id}/documents/{doc_id}")
async def delete_document(kb_id: int, doc_id: str):
    """Delete a document"""
    # Find the document
    doc_to_delete = None
    for doc in _documents.values():
        if doc.get("doc_id") == doc_id:
            doc_to_delete = doc
            break

    if not doc_to_delete:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc_to_delete["kb_id"] != kb_id:
        raise HTTPException(status_code=400, detail="Document does not belong to this knowledge base")

    # Delete from knowledge base (Milvus)
    kb_service.delete_document(kb_id, doc_id)

    # Remove from storage
    del _documents[doc_to_delete["id"]]

    return {"message": "Document deleted successfully"}
