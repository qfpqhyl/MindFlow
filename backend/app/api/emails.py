"""
Email notifications API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas import EmailNotificationResponse, APIResponse
from app.database import db
from app.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/emails/notifications", tags=["Email Notifications"])


@router.get("", response_model=APIResponse)
async def get_email_notifications(
    task_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get email notification history
    """
    with db.get_connection() as conn:
        # Build query
        base_query = """
            FROM email_notifications en
            JOIN tasks t ON en.task_id = t.task_id
            WHERE t.user_id = ?
        """
        params = [current_user["user_id"]]

        if task_id:
            base_query += " AND en.task_id = ?"
            params.append(task_id)

        # Get total count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Get notifications
        offset = (page - 1) * page_size
        query = f"""
            SELECT
                en.notification_id, en.task_id, en.recipient_email, en.status,
                en.sent_at, en.error_message,
                t.title as task_title
            {base_query}
            ORDER BY en.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        cursor = conn.execute(query, params)
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                "notification_id": row["notification_id"],
                "task_id": row["task_id"],
                "task_title": row["task_title"],
                "recipient_email": row["recipient_email"],
                "status": row["status"],
                "sent_at": row["sent_at"],
                "error_message": row["error_message"]
            })

    return APIResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "items": notifications
        }
    )
