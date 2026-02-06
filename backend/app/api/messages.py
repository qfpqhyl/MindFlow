"""
Messages API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from app.schemas import MessageCreate, MessageResponse, MessageSendResponse, APIResponse
from app.database import db
from app.ai_service import nvidia_service
from app.dependencies import get_current_user, get_user_settings
from typing import Optional
from datetime import datetime
import json

router = APIRouter(prefix="/conversations/{conversation_id}/messages", tags=["Messages"])


async def verify_conversation_ownership(conversation_id: str, user_id: str) -> bool:
    """Verify user owns the conversation"""
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT user_id FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        conversation = cursor.fetchone()
        return conversation and conversation["user_id"] == user_id


@router.get("", response_model=APIResponse)
async def get_messages(
    conversation_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get messages in a conversation
    """
    if not await verify_conversation_ownership(conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    with db.get_connection() as conn:
        # Get total count
        cursor = conn.execute("""
            SELECT COUNT(*) as total FROM messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        total = cursor.fetchone()["total"]

        # Get messages
        offset = (page - 1) * page_size
        cursor = conn.execute("""
            SELECT message_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            LIMIT ? OFFSET ?
        """, (conversation_id, page_size, offset))

        messages = [dict(msg) for msg in cursor.fetchall()]

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "items": messages
        }
    )


@router.post("/stream")
async def send_message_stream(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message and get AI streaming response (SSE)
    """
    if not await verify_conversation_ownership(conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    now = datetime.utcnow()

    # Save user message
    user_message_id = db.generate_uuid()
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (message_id, conversation_id, role, content, created_at)
            VALUES (?, ?, 'user', ?, ?)
        """, (user_message_id, conversation_id, message_data.content, now))

        # Update conversation updated_at
        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
        """, (now, conversation_id))

        # Get conversation history
        cursor = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in cursor.fetchall()
        ]

    async def stream_generator():
        """Generate SSE stream"""
        try:
            # Get user's preferred model
            user_settings = await get_user_settings(current_user["user_id"])
            user_model = user_settings.get("default_model_id") or "minimaxai/minimax-m2.1"

            # Stream AI response with user's preferred model
            ai_response = ""
            async for chunk in nvidia_service.chat(messages, model=user_model, stream=True):
                if chunk.startswith("Error:"):
                    # Handle error
                    yield f"event: error\ndata: {json.dumps({'message': chunk})}\n\n"
                    return

                ai_response += chunk
                # Send each chunk as SSE event
                yield f"event: chunk\ndata: {json.dumps({'content': chunk})}\n\n"

            # Save assistant message
            assistant_message_id = db.generate_uuid()
            with db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO messages (message_id, conversation_id, role, content, created_at)
                    VALUES (?, ?, 'assistant', ?, ?)
                """, (assistant_message_id, conversation_id, ai_response, datetime.utcnow()))

                # Update conversation updated_at
                conn.execute("""
                    UPDATE conversations
                    SET updated_at = ?
                    WHERE conversation_id = ?
                """, (datetime.utcnow(), conversation_id))

            # Send completion event
            yield f"event: complete\ndata: {json.dumps({'message_id': assistant_message_id, 'created_at': datetime.utcnow().isoformat()})}\n\n"

        except Exception as e:
            # Send error event
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("", response_model=APIResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message and get AI response
    """
    if not await verify_conversation_ownership(conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    now = datetime.utcnow()

    # Save user message
    user_message_id = db.generate_uuid()
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (message_id, conversation_id, role, content, created_at)
            VALUES (?, ?, 'user', ?, ?)
        """, (user_message_id, conversation_id, message_data.content, now))

        # Update conversation updated_at
        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
        """, (now, conversation_id))

        # Get conversation history
        cursor = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in cursor.fetchall()
        ]

    # Get user's preferred model
    user_settings = await get_user_settings(current_user["user_id"])
    user_model = user_settings.get("default_model_id") or "minimaxai/minimax-m2.1"

    # Get AI response
    ai_response = ""
    if message_data.stream:
        # Streaming response (would need SSE implementation)
        async for chunk in nvidia_service.chat(messages, model=user_model):
            ai_response += chunk
    else:
        async for chunk in nvidia_service.chat(messages, model=user_model, stream=False):
            ai_response += chunk

    # Save assistant message
    assistant_message_id = db.generate_uuid()
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (message_id, conversation_id, role, content, created_at)
            VALUES (?, ?, 'assistant', ?, ?)
        """, (assistant_message_id, conversation_id, ai_response, datetime.utcnow()))

        # Update conversation updated_at
        conn.execute("""
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
        """, (datetime.utcnow(), conversation_id))

    return APIResponse(
        code=200,
        message="success",
        data={
            "user_message": {
                "message_id": user_message_id,
                "role": "user",
                "content": message_data.content,
                "created_at": now
            },
            "assistant_message": {
                "message_id": assistant_message_id,
                "role": "assistant",
                "content": ai_response,
                "created_at": datetime.utcnow()
            }
        }
    )


@router.delete("/{message_id}", response_model=APIResponse)
async def delete_message(
    message_id: str,
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a message
    """
    if not await verify_conversation_ownership(conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    with db.get_connection() as conn:
        # Delete message
        conn.execute("""
            DELETE FROM messages
            WHERE message_id = ? AND conversation_id = ?
        """, (message_id, conversation_id))

    return APIResponse(
        code=200,
        message="删除成功"
    )
