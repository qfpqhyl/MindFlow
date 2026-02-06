"""
Conversations API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationDetail, APIResponse
)
from app.database import db
from app.dependencies import get_current_user
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=APIResponse)
async def get_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of conversations
    """
    with db.get_connection() as conn:
        # Build query
        base_query = "FROM conversations WHERE user_id = ?"
        params = [current_user["user_id"]]

        if keyword:
            base_query += " AND title LIKE ?"
            params.append(f"%{keyword}%")

        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Get conversations with message count
        offset = (page - 1) * page_size
        query = f"""
            SELECT
                c.*,
                (SELECT COUNT(*) FROM messages WHERE conversation_id = c.conversation_id) as message_count
            FROM conversations c
            WHERE c.user_id = ?
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
        """

        if keyword:
            query = f"""
                SELECT
                    c.*,
                    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.conversation_id) as message_count
                FROM conversations c
                WHERE c.user_id = ? AND c.title LIKE ?
                ORDER BY c.updated_at DESC
                LIMIT ? OFFSET ?
            """
            cursor = conn.execute(query, [current_user["user_id"], f"%{keyword}%", page_size, offset])
        else:
            cursor = conn.execute(query, [current_user["user_id"], page_size, offset])

        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "conversation_id": row["conversation_id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            })

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": conversations
        }
    )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conv_data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new conversation
    """
    conversation_id = db.generate_uuid()
    now = datetime.utcnow()

    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO conversations (conversation_id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, current_user["user_id"], conv_data.title, now, now))

    return APIResponse(
        code=201,
        message="创建成功",
        data={
            "conversation_id": conversation_id,
            "title": conv_data.title,
            "created_at": now
        }
    )


@router.get("/{conversation_id}", response_model=APIResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation details with messages
    """
    with db.get_connection() as conn:
        # Get conversation
        cursor = conn.execute("""
            SELECT * FROM conversations
            WHERE conversation_id = ? AND user_id = ?
        """, (conversation_id, current_user["user_id"]))

        conversation = cursor.fetchone()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        cursor = conn.execute("""
            SELECT message_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        messages = [dict(msg) for msg in cursor.fetchall()]

    return APIResponse(
        code=200,
        message="success",
        data={
            "conversation_id": conversation["conversation_id"],
            "title": conversation["title"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "messages": messages
        }
    )


@router.put("/{conversation_id}", response_model=APIResponse)
async def update_conversation(
    conversation_id: str,
    conv_data: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update conversation title
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))

        conversation = cursor.fetchone()
        if not conversation or conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Update
        conn.execute("""
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE conversation_id = ?
        """, (conv_data.title, datetime.utcnow(), conversation_id))

    return APIResponse(
        code=200,
        message="更新成功",
        data={
            "conversation_id": conversation_id,
            "title": conv_data.title
        }
    )


@router.delete("/{conversation_id}", response_model=APIResponse)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))

        conversation = cursor.fetchone()
        if not conversation or conversation["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Delete messages first (foreign key constraint)
        conn.execute("""
            DELETE FROM messages
            WHERE conversation_id = ?
        """, (conversation_id,))

        # Delete conversation
        conn.execute("""
            DELETE FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))

    return APIResponse(
        code=200,
        message="删除成功"
    )
