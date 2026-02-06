"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import (
    UserRegister, UserLogin, ChangePassword, TokenResponse,
    RefreshTokenResponse, APIResponse, ErrorResponse
)
from app.database import db
from app.auth import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    """
    # Check if username exists
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (user_data.username,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email exists
        cursor = conn.execute(
            "SELECT user_id FROM users WHERE email = ?",
            (user_data.email,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Create user
        user_id = db.generate_uuid()
        password_hash = get_password_hash(user_data.password)
        now = datetime.utcnow()

        conn.execute("""
            INSERT INTO users (user_id, username, email, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_data.username, user_data.email, password_hash, now, now))

        # Create default settings
        setting_id = db.generate_uuid()
        conn.execute("""
            INSERT INTO user_settings (setting_id, user_id, default_email, reminder_enabled)
            VALUES (?, ?, ?, 1)
        """, (setting_id, user_id, user_data.email))

    # Generate token
    token = create_access_token({"sub": user_id})

    return APIResponse(
        code=201,
        message="注册成功",
        data={
            "user_id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "token": token
        }
    )


@router.post("/login", response_model=APIResponse)
async def login(user_data: UserLogin):
    """
    Login user
    """
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT user_id, username, email, password_hash FROM users WHERE username = ?",
            (user_data.username,)
        )
        user = cursor.fetchone()

        if not user or not verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Update last login
        conn.execute(
            "UPDATE users SET updated_at = ? WHERE user_id = ?",
            (datetime.utcnow(), user["user_id"])
        )

    token = create_access_token({"sub": user["user_id"]})

    return APIResponse(
        code=200,
        message="登录成功",
        data={
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "token": token
        }
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    Refresh access token
    """
    token = create_access_token({"sub": current_user["user_id"]})

    return APIResponse(
        code=200,
        message="刷新成功",
        data={"token": token}
    )
