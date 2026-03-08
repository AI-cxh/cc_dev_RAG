"""Schemas for chat operations"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""

    conversation_id: Optional[int] = Field(
        default=None, description="Conversation ID (None for new conversation)"
    )
    message: str = Field(..., description="User message")
    kb_id: Optional[int] = Field(default=None, description="Knowledge base ID to use")
    stream: bool = Field(default=True, description="Enable streaming response")


class ChatChunk(BaseModel):
    """Schema for streaming chunk"""

    type: str = Field(..., description="Chunk type: 'content', 'reference', 'done', 'error'")
    content: Optional[str] = Field(default=None, description="Content chunk")
    reference: Optional[dict] = Field(default=None, description="Reference data")
    error: Optional[str] = Field(default=None, description="Error message")


class Reference(BaseModel):
    """Schema for document reference"""

    id: int = Field(..., description="Reference ID")
    doc_id: str = Field(..., description="Document ID")
    doc_name: str = Field(..., description="Document name")
    chunk_index: int = Field(..., description="Chunk index")
    page_num: Optional[int] = Field(default=None, description="Page number")
    content: str = Field(..., description="Original content snippet")
    similarity_score: Optional[float] = Field(default=None, description="Similarity score")


class ChatResponse(BaseModel):
    """Schema for complete chat response"""

    conversation_id: int
    answer: str
    references: list[Reference] = Field(default_factory=list)
    used_web_search: bool = Field(default=False)
