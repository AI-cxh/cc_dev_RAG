"""Chat API endpoints"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio

from app.models import db_manager
from app.schemas import ChatRequest, ChatResponse, Reference
from app.graph.agent import create_agent

router = APIRouter()


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    Stream chat response with SSE

    This endpoint uses the LangGraph agent for intelligent responses
    """
    async def event_generator():
        try:
            # Get or create conversation
            if request.conversation_id:
                conversation = await db_manager.get_conversation(request.conversation_id)
                if not conversation:
                    yield f"data: {json.dumps({'type': 'error', 'error': 'Conversation not found'})}\n\n"
                    return
            else:
                conversation = await db_manager.create_conversation()

            # Save user message
            await db_manager.create_message(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
            )

            # Send conversation ID
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"

            # Create agent
            agent = create_agent(kb_id=request.kb_id)

            # Stream response
            full_answer = ""
            references = []

            async for chunk in agent.stream(request.message, kb_id=request.kb_id):
                chunk_data = json.dumps(chunk, ensure_ascii=False)
                yield f"data: {chunk_data}\n\n"

                if chunk.get("type") == "content":
                    full_answer += chunk.get("content", "")
                elif chunk.get("type") == "references":
                    references = chunk.get("references", [])

            # Save assistant message
            if full_answer:
                await db_manager.create_message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_answer,
                    metadata={"references": references} if references else None,
                )

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint

    Uses the LangGraph agent for intelligent responses
    """
    # Get or create conversation
    if request.conversation_id:
        conversation = await db_manager.get_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = await db_manager.create_conversation()

    # Save user message
    await db_manager.create_message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    # Create agent and invoke
    agent = create_agent(kb_id=request.kb_id)
    result = await agent.invoke(request.message, kb_id=request.kb_id)

    # Save assistant message
    if result.get("answer"):
        await db_manager.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            metadata={"references": result.get("references")} if result.get("references") else None,
        )

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.get("answer", "No response generated"),
        references=result.get("references", []),
        used_web_search=result.get("used_web_search", False),
    )


@router.get("/conversations")
async def list_conversations(limit: int = 50, offset: int = 0):
    """List all conversations"""
    conversations = await db_manager.list_conversations(limit=limit, offset=offset)
    return [{
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
    } for conv in conversations]


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    """Get conversation details with messages"""
    conversation = await db_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await db_manager.get_conversation_messages(conversation_id)
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages,
    }


@router.post("/conversations")
async def create_conversation(title: str = "New Conversation"):
    """Create a new conversation"""
    conversation = await db_manager.create_conversation(title=title)
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """Delete a conversation"""
    success = await db_manager.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}


async def _stream_placeholder(message: str):
    """Placeholder streaming function (deprecated - use actual agent)"""
    import asyncio
    import json

    response = {"type": "content", "content": "[Placeholder response]"}
    yield f"data: {json.dumps(response)}\n\n"
    await asyncio.sleep(0.1)

    done = {"type": "done"}
    yield f"data: {json.dumps(done)}\n\n"
