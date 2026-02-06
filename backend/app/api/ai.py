"""
AI configuration API routes
"""
from fastapi import APIRouter, Depends
from app.schemas import ModelInfo, ModelsListResponse, SetDefaultModel, APIResponse
from app.database import db
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["AI Configuration"])

# Available AI models
AVAILABLE_MODELS = [
    {
        "id": "z-ai/glm4.7",
        "name": "智谱 GLM-4.7",
        "provider": "z-ai",
        "description": "智谱 AI 最新发布的 GLM-4.7 模型"
    },
    {
        "id": "minimaxai/minimax-m2.1",
        "name": "MiniMax M2.1",
        "provider": "minimaxai",
        "description": "MiniMax AI 的 M2.1 模型"
    },
    {
        "id": "moonshotai/kimi-k2.5",
        "name": "Kimi K2.5",
        "provider": "moonshotai",
        "description": "Moonshot AI 的 Kimi K2.5 模型"
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
