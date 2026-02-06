"""
FastAPI dependencies and authentication middleware
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.database import db
from app.auth import decode_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT user_id, username, email, created_at FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return dict(user)


async def get_user_settings(user_id: str) -> dict:
    """
    Get user settings

    Args:
        user_id: User ID

    Returns:
        dict: User settings
    """
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT default_email, reminder_enabled, default_model_id
            FROM user_settings
            WHERE user_id = ?
        """, (user_id,))

        settings_row = cursor.fetchone()

        if settings_row:
            return dict(settings_row)
        else:
            # Create default settings
            return {
                "default_email": None,
                "reminder_enabled": True,
                "default_model_id": "minimaxai/minimax-m2.1"
            }
