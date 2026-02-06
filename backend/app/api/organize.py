"""
Organize API routes - Convert conversations to documents
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    OrganizeToDocument, OrganizeResponse, OrganizeSuggestionsResponse, APIResponse
)
from app.database import db
from app.ai_service import nvidia_service
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/organize", tags=["Organize"])


async def verify_conversation_ownership(conversation_id: str, user_id: str) -> bool:
    """Verify user owns the conversation"""
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT user_id FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        conversation = cursor.fetchone()
        return conversation and conversation["user_id"] == user_id


@router.post("/to-document", response_model=APIResponse)
async def organize_to_document(
    organize_data: OrganizeToDocument,
    current_user: dict = Depends(get_current_user)
):
    """
    Organize conversation content into a document
    Optionally create a task with reminder
    """
    # Verify ownership
    if not await verify_conversation_ownership(organize_data.conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get conversation messages
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (organize_data.conversation_id,))

        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in cursor.fetchall()
        ]

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation has no messages"
            )

    # Generate summary if not provided
    summary = organize_data.summary
    if not summary:
        summary = await nvidia_service.generate_summary(messages)

    # Generate document content
    content = await nvidia_service.generate_document(messages, organize_data.title)

    # Generate tags
    tags = await nvidia_service.suggest_tags(content)

    # Create document
    document_id = db.generate_uuid()
    now = datetime.utcnow()

    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO documents
            (document_id, user_id, title, content, summary, source_conversation_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document_id,
            current_user["user_id"],
            organize_data.title,
            content,
            summary,
            organize_data.conversation_id,
            now,
            now
        ))

        # Add tags
        for tag in tags:
            tag_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO document_tags (tag_id, document_id, tag_name)
                VALUES (?, ?, ?)
            """, (tag_id, document_id, tag))

    # Create task if requested
    task_id = None
    if organize_data.create_task and organize_data.task_config:
        task_id = db.generate_uuid()

        # Use reminder email from config or user default
        reminder_email = organize_data.task_config.reminder_email
        if not reminder_email:
            cursor = conn.execute("""
                SELECT default_email FROM user_settings
                WHERE user_id = ?
            """, (current_user["user_id"],))
            settings_row = cursor.fetchone()
            reminder_email = settings_row["default_email"] if settings_row else None

        conn.execute("""
            INSERT INTO tasks
            (task_id, user_id, title, description, due_date, reminder_enabled,
             reminder_email, source_document_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            current_user["user_id"],
            organize_data.title,
            summary,
            organize_data.task_config.due_date,
            organize_data.task_config.reminder_enabled,
            reminder_email,
            document_id,
            now,
            now
        ))

    return APIResponse(
        code=200,
        message="整理成功",
        data={
            "document_id": document_id,
            "document_url": f"/documents/{document_id}",
            "task_id": task_id,
            "task_url": f"/tasks/{task_id}" if task_id else None
        }
    )


@router.post("/suggestions", response_model=APIResponse)
async def get_organize_suggestions(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-generated suggestions for organizing conversation to document
    """
    # Verify ownership
    if not await verify_conversation_ownership(conversation_id, current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get conversation messages
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in cursor.fetchall()
        ]

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation has no messages"
            )

    # Generate summary
    summary = await nvidia_service.generate_summary(messages)

    # Generate title suggestion
    title_prompt = [
        {
            "role": "system",
            "content": "你是一个标题生成助手。请为对话生成一个简洁、准确的标题（不超过20字）。只返回标题，不要其他内容。"
        },
        {
            "role": "user",
            "content": f"为以下对话生成标题：\n\n{summary}"
        }
    ]

    title_response = ""
    async for chunk in nvidia_service.chat(title_prompt, stream=False):
        title_response += chunk
    suggested_title = title_response.strip()

    # Extract key points
    key_points_prompt = [
        {
            "role": "system",
            "content": "你是一个关键点提取助手。请从对话中提取3-5个关键点，每个点用一句话概括，每行一个。只返回关键点，不要其他内容。"
        },
        {
            "role": "user",
            "content": f"从以下对话中提取关键点：\n\n{summary}"
        }
    ]

    key_points_response = ""
    async for chunk in nvidia_service.chat(key_points_prompt, stream=False):
        key_points_response += chunk
    key_points = [
        point.strip()
        for point in key_points_response.strip().split("\n")
        if point.strip()
    ][:5]

    # Generate tags
    tags = await nvidia_service.suggest_tags(summary)

    return APIResponse(
        code=200,
        message="success",
        data={
            "summary": summary,
            "suggested_title": suggested_title,
            "key_points": key_points,
            "suggested_tags": tags
        }
    )
