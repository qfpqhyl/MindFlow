"""
AI configuration API routes
"""
from fastapi import APIRouter, Depends
from app.schemas import ModelInfo, ModelsListResponse, SetDefaultModel, APIResponse
from app.database import db
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["AI Configuration"])

# Available NVIDIA models
AVAILABLE_MODELS = [
    {
        "id": "meta/llama-3.1-405b-instruct",
        "name": "Llama 3.1 405B Instruct",
        "provider": "nvidia"
    },
    {
        "id": "meta/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B Instruct",
        "provider": "nvidia"
    },
    {
        "id": "meta/llama-3.1-8b-instruct",
        "name": "Llama 3.1 8B Instruct",
        "provider": "nvidia"
    },
    {
        "id": "mistralai/mistral-large",
        "name": "Mistral Large",
        "provider": "nvidia"
    },
    {
        "id": "google/gemma-2-27b-it",
        "name": "Gemma 2 27B IT",
        "provider": "nvidia"
    }
]


@router.get("/models", response_model=APIResponse)
async def get_models(current_user: dict = Depends(get_current_user)):
    """
    Get list of available AI models
    """
    return APIResponse(
        code=200,
        message="success",
        data={
            "models": AVAILABLE_MODELS
        }
    )


@router.put("/models/default", response_model=APIResponse)
async def set_default_model(
    model_data: SetDefaultModel,
    current_user: dict = Depends(get_current_user)
):
    """
    Set default AI model for user
    """
    # Validate model exists
    model_exists = any(m["id"] == model_data.model_id for m in AVAILABLE_MODELS)
    if not model_exists:
        return APIResponse(
            code=400,
            message="Invalid model ID",
            data=None
        )

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
                SET default_model_id = ?
                WHERE user_id = ?
            """, (model_data.model_id, current_user["user_id"]))
        else:
            # Create
            setting_id = db.generate_uuid()
            conn.execute("""
                INSERT INTO user_settings (setting_id, user_id, default_model_id, reminder_enabled)
                VALUES (?, ?, ?, 1)
            """, (setting_id, current_user["user_id"], model_data.model_id))

    # Get model name
    model_name = next((m["name"] for m in AVAILABLE_MODELS if m["id"] == model_data.model_id), model_data.model_id)

    return APIResponse(
        code=200,
        message="设置成功",
        data={
            "model_id": model_data.model_id,
            "model_name": model_name
        }
    )
