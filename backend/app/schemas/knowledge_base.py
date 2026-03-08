"""Schemas for knowledge base operations"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating a knowledge base"""

    name: str = Field(..., min_length=1, max_length=100, description="Knowledge base name")
    description: Optional[str] = Field("", max_length=500, description="Knowledge base description")


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response"""

    id: int
    name: str
    description: str
    document_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentMetadata(BaseModel):
    """Schema for document metadata"""

    total_chunks: int
    chunk_size: int
    parse_time: float
    file_type: str
    file_size: int


class DocumentResponse(BaseModel):
    """Schema for document response"""

    id: int
    kb_id: int
    doc_name: str
    file_type: str
    file_size: int
    status: str  # 'processing', 'completed', 'failed'
    metadata: Optional[DocumentMetadata] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadProgress(BaseModel):
    """Schema for upload progress"""

    stage: str  # 'uploading', 'parsing', 'embedding', 'completed', 'failed'
    progress: float  # 0.0 to 1.0
    message: str


class UploadDocumentResponse(BaseModel):
    """Schema for document upload response"""

    document_id: int
    status: str
    progress: UploadProgress
