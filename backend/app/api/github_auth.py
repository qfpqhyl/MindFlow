"""
GitHub OAuth API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from app.config import get_settings
from app.schemas import APIResponse
from app.database import db
from app.auth import create_access_token
from app.dependencies import get_current_user
from datetime import datetime
import httpx
import json

router = APIRouter(prefix="/auth/github", tags=["GitHub OAuth"])

settings = get_settings()


@router.get("/login")
async def github_login():
    """
    Redirect to GitHub OAuth page
    """
    github_client_id = settings.github_client_id

    if not github_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )

    # GitHub OAuth URL
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={github_client_id}"
        f"&scope=user:email"
        f"&redirect_uri={settings.github_oauth_redirect_uri}"
    )

    return RedirectResponse(auth_url)


@router.get("/callback")
async def github_callback(code: str):
    """
    Handle GitHub OAuth callback
    """
    github_client_id = settings.github_client_id
    github_client_secret = settings.github_client_secret

    if not github_client_id or not github_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth not configured"
        )

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        # Get access token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": github_client_id,
                "client_secret": github_client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"}
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from GitHub"
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token in response"
            )

        # Get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from GitHub"
            )

        github_user = user_response.json()

        # Get user email
        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )

        emails = []
        if email_response.status_code == 200:
            emails = email_response.json()

        # Find primary email
        primary_email = github_user.get("email")
        if not primary_email and emails:
            primary_email = next(
                (e.get("email") for e in emails if e.get("primary")),
                None
            )
        if not primary_email and emails:
            primary_email = emails[0].get("email")

        if not primary_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required but not provided by GitHub"
            )

        # Check if user exists by GitHub ID
        username = None  # Initialize username variable

        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT user_id, username, email FROM users WHERE github_id = ?",
                (str(github_user.get("id")),)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                # User exists, update info and login
                user_id = existing_user["user_id"]
                username = existing_user["username"]
                conn.execute(
                    "UPDATE users SET updated_at = ? WHERE user_id = ?",
                    (datetime.utcnow(), user_id)
                )
            else:
                # Create new user
                user_id = db.generate_uuid()
                username = github_user.get("login")
                now = datetime.utcnow()

                # Check if username already exists
                cursor = conn.execute(
                    "SELECT user_id FROM users WHERE username = ?",
                    (username,)
                )
                if cursor.fetchone():
                    username = f"{username}_{github_user.get('id')}"

                # Check if email already exists
                cursor = conn.execute(
                    "SELECT user_id, username FROM users WHERE email = ?",
                    (primary_email,)
                )
                existing_email_user = cursor.fetchone()
                if existing_email_user:
                    # Email exists, link GitHub account
                    user_id = existing_email_user["user_id"]
                    username = existing_email_user["username"]
                    conn.execute(
                        "UPDATE users SET github_id = ?, avatar_url = ?, updated_at = ? WHERE user_id = ?",
                        (str(github_user.get("id")), github_user.get("avatar_url"), datetime.utcnow(), user_id)
                    )
                else:
                    # Create new user
                    conn.execute("""
                        INSERT INTO users (user_id, username, email, github_id, avatar_url, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        username,
                        primary_email,
                        str(github_user.get("id")),
                        github_user.get("avatar_url"),
                        now,
                        now
                    ))

                    # Create default settings
                    setting_id = db.generate_uuid()
                    conn.execute("""
                        INSERT INTO user_settings (setting_id, user_id, default_email, reminder_enabled)
                        VALUES (?, ?, ?, 1)
                    """, (setting_id, user_id, primary_email))

        # Generate token
        token = create_access_token({"sub": user_id})

        # Redirect to frontend with token
        return RedirectResponse(
            f"{settings.github_oauth_frontend_success_url}?token={token}&username={username}"
        )


@router.get("/me", response_model=APIResponse)
async def get_github_user(current_user: dict = Depends(get_current_user)):
    """
    Get current user info
    """
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT user_id, username, email, github_id, avatar_url FROM users WHERE user_id = ?",
            (current_user["user_id"],)
        )
        user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return APIResponse(
        code=200,
        message="success",
        data={
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "github_id": user["github_id"],
            "avatar_url": user["avatar_url"]
        }
    )
