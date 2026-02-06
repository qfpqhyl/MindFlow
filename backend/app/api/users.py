"""
Users API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import UserResponse, UserUpdate, ChangePassword, EmailSettingsUpdate, APIResponse
from app.database import db
from app.auth import verify_password, get_password_hash
from app.dependencies import get_current_user, get_user_settings
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse)
async def get_user_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    settings = await get_user_settings(current_user["user_id"])

    return APIResponse(
        code=200,
        message="success",
        data={
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "created_at": current_user["created_at"],
            "settings": settings
        }
    )


@router.put("/me", response_model=APIResponse)
async def update_user_me(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user information
    """
    with db.get_connection() as conn:
        # Build update query
        updates = []
        params = []

        if user_data.username:
            # Check if username already exists
            cursor = conn.execute(
                "SELECT user_id FROM users WHERE username = ? AND user_id != ?",
                (user_data.username, current_user["user_id"])
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            updates.append("username = ?")
            params.append(user_data.username)

        if user_data.email:
            # Check if email already exists
            cursor = conn.execute(
                "SELECT user_id FROM users WHERE email = ? AND user_id != ?",
                (user_data.email, current_user["user_id"])
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            updates.append("email = ?")
            params.append(user_data.email)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.utcnow())
            params.append(current_user["user_id"])

            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
            conn.execute(query, params)

            # Fetch updated user
            cursor = conn.execute(
                "SELECT user_id, username, email FROM users WHERE user_id = ?",
                (current_user["user_id"],)
            )
            updated_user = cursor.fetchone()

            return APIResponse(
                code=200,
                message="更新成功",
                data={
                    "user_id": updated_user["user_id"],
                    "username": updated_user["username"],
                    "email": updated_user["email"]
                }
            )

        return APIResponse(
            code=200,
            message="更新成功",
            data={
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "email": current_user["email"]
            }
        )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """
    Change user password
    """
    # Get current password hash
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT password_hash FROM users WHERE user_id = ?",
            (current_user["user_id"],)
        )
        user = cursor.fetchone()

        if not user or not verify_password(password_data.old_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        new_password_hash = get_password_hash(password_data.new_password)
        conn.execute("""
            UPDATE users
            SET password_hash = ?, updated_at = ?
            WHERE user_id = ?
        """, (new_password_hash, datetime.utcnow(), current_user["user_id"]))

    return APIResponse(
        code=200,
        message="密码修改成功"
    )


@router.put("/email-settings", response_model=APIResponse)
async def update_email_settings(
    settings_data: EmailSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update email notification settings
    """
    with db.get_connection() as conn:
        # Check if settings exist
        cursor = conn.execute(
            "SELECT setting_id FROM user_settings WHERE user_id = ?",
            (current_user["user_id"],)
        )
        settings_row = cursor.fetchone()

        if settings_row:
            # Update
            conn.execute("""
                UPDATE user_settings
                SET default_email = ?, reminder_enabled = ?
                WHERE user_id = ?
            """, (settings_data.default_email, settings_data.reminder_enabled, current_user["user_id"]))
        else:
            # Create
            setting_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO user_settings (setting_id, user_id, default_email, reminder_enabled)
                VALUES (?, ?, ?, ?)
            """, (setting_id, current_user["user_id"], settings_data.default_email, settings_data.reminder_enabled))

    return APIResponse(
        code=200,
        message="配置已更新",
        data={
            "default_email": settings_data.default_email,
            "reminder_enabled": settings_data.reminder_enabled
        }
    )
