"""
Tasks API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskDetail, APIResponse
)
from app.database import db
from app.email_service import email_service
from app.dependencies import get_current_user
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=APIResponse)
async def get_tasks(
    status_filter: Optional[str] = Query(None, regex="^(pending|completed|overdue)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of tasks
    """
    with db.get_connection() as conn:
        # Build query
        base_query = "FROM tasks WHERE user_id = ?"
        params = [current_user["user_id"]]

        if status_filter:
            base_query += " AND status = ?"
            params.append(status_filter)

        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Get tasks
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM tasks
            WHERE user_id = {'' if status_filter else '?'}
            {f"AND status = ?" if status_filter else ""}
            ORDER BY due_date ASC
            LIMIT ? OFFSET ?
        """

        if status_filter:
            cursor = conn.execute(query, [current_user["user_id"], status_filter, page_size, offset])
        else:
            cursor = conn.execute(query, [current_user["user_id"], page_size, offset])

        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "task_id": row["task_id"],
                "title": row["title"],
                "description": row["description"],
                "due_date": row["due_date"],
                "status": row["status"],
                "reminder_enabled": bool(row["reminder_enabled"]),
                "reminder_email": row["reminder_email"],
                "source_document_id": row["source_document_id"],
                "created_at": row["created_at"]
            })

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "items": tasks
        }
    )


@router.get("/{task_id}", response_model=APIResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get task details
    """
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM tasks
            WHERE task_id = ? AND user_id = ?
        """, (task_id, current_user["user_id"]))

        task = cursor.fetchone()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

    return APIResponse(
        code=200,
        message="success",
        data={
            "task_id": task["task_id"],
            "title": task["title"],
            "description": task["description"],
            "due_date": task["due_date"],
            "status": task["status"],
            "reminder_enabled": bool(task["reminder_enabled"]),
            "reminder_email": task["reminder_email"],
            "source_document_id": task["source_document_id"],
            "email_sent": bool(task["email_sent"]),
            "created_at": task["created_at"],
            "updated_at": task["updated_at"]
        }
    )


@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new task
    """
    task_id = db.generate_uuid()
    now = datetime.utcnow()

    # Use provided email or user default
    reminder_email = task_data.reminder_email
    if not reminder_email:
        with db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT default_email FROM user_settings
                WHERE user_id = ?
            """, (current_user["user_id"],))
            settings_row = cursor.fetchone()
            reminder_email = settings_row["default_email"] if settings_row else None

    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO tasks
            (task_id, user_id, title, description, due_date, reminder_enabled,
             reminder_email, source_document_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            current_user["user_id"],
            task_data.title,
            task_data.description,
            task_data.due_date,
            task_data.reminder_enabled,
            reminder_email,
            task_data.source_document_id,
            now,
            now
        ))

    return APIResponse(
        code=201,
        message="创建成功",
        data={
            "task_id": task_id,
            "title": task_data.title,
            "due_date": task_data.due_date
        }
    )


@router.put("/{task_id}", response_model=APIResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a task
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM tasks
            WHERE task_id = ?
        """, (task_id,))

        task = cursor.fetchone()
        if not task or task["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Build update query
        updates = []
        params = []
        if task_data.title:
            updates.append("title = ?")
            params.append(task_data.title)
        if task_data.description is not None:
            updates.append("description = ?")
            params.append(task_data.description)
        if task_data.due_date:
            updates.append("due_date = ?")
            params.append(task_data.due_date)
        if task_data.status:
            updates.append("status = ?")
            params.append(task_data.status)
        if task_data.reminder_enabled is not None:
            updates.append("reminder_enabled = ?")
            params.append(task_data.reminder_enabled)
        if task_data.reminder_email is not None:
            updates.append("reminder_email = ?")
            params.append(task_data.reminder_email)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow())
            params.append(task_id)

            query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
            conn.execute(query, params)

    return APIResponse(
        code=200,
        message="更新成功",
        data={
            "task_id": task_id,
            "updated_at": datetime.utcnow()
        }
    )


@router.post("/{task_id}/complete", response_model=APIResponse)
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a task as completed
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id, status FROM tasks
            WHERE task_id = ?
        """, (task_id,))

        task = cursor.fetchone()
        if not task or task["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        now = datetime.utcnow()
        conn.execute("""
            UPDATE tasks
            SET status = 'completed', updated_at = ?
            WHERE task_id = ?
        """, (now, task_id))

    return APIResponse(
        code=200,
        message="任务已完成",
        data={
            "task_id": task_id,
            "status": "completed",
            "completed_at": now
        }
    )


@router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a task
    """
    with db.get_connection() as conn:
        # Check ownership
        cursor = conn.execute("""
            SELECT user_id FROM tasks
            WHERE task_id = ?
        """, (task_id,))

        task = cursor.fetchone()
        if not task or task["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Delete notifications first
        conn.execute("""
            DELETE FROM email_notifications
            WHERE task_id = ?
        """, (task_id,))

        # Delete task
        conn.execute("""
            DELETE FROM tasks
            WHERE task_id = ?
        """, (task_id,))

    return APIResponse(
        code=200,
        message="删除成功"
    )


@router.post("/{task_id}/send-reminder", response_model=APIResponse)
async def send_task_reminder(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually send a task reminder email
    """
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT t.*, u.email as user_email
            FROM tasks t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.task_id = ? AND t.user_id = ?
        """, (task_id, current_user["user_id"]))

        task = cursor.fetchone()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Use reminder email if set, otherwise use user email
        recipient = task["reminder_email"] or task["user_email"]

        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email address configured for this task"
            )

        # Format due date
        due_date = task["due_date"]
        if isinstance(due_date, str):
            due_date_str = due_date
        else:
            due_date_str = due_date.strftime("%Y-%m-%d %H:%M")

        # Send email
        success = await email_service.send_task_reminder(
            to_email=recipient,
            task_title=task["title"],
            task_description=task["description"],
            due_date=due_date_str
        )

        now = datetime.utcnow()
        if success:
            # Record notification
            notification_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO email_notifications
                (notification_id, task_id, recipient_email, status, sent_at)
                VALUES (?, ?, ?, 'sent', ?)
            """, (notification_id, task_id, recipient, now))

            # Mark email as sent
            conn.execute("""
                UPDATE tasks
                SET email_sent = 1
                WHERE task_id = ?
            """, (task_id,))

            return APIResponse(
                code=200,
                message="提醒邮件已发送",
                data={
                    "task_id": task_id,
                    "email_sent": True,
                    "sent_at": now
                }
            )
        else:
            # Record failed notification
            notification_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO email_notifications
                (notification_id, task_id, recipient_email, status, error_message)
                VALUES (?, ?, ?, 'failed', 'Failed to send email')
            """, (notification_id, task_id, recipient))

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reminder email"
            )
