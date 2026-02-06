"""
MindFlow Backend Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    db_file: str = "./data/mindflow.db"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    # JWT Settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # NVIDIA API
    nvidia_api_key: str
    nvidia_api_base_url: str = "https://integrate.api.nvidia.com/v1/chat/completions"
    default_model: str = "meta/llama-3.1-405b-instruct"

    # Email Settings
    smtp_host: str = "smtp.feishu.cn"
    smtp_port: int = 465
    smtp_username: str
    smtp_password: str
    email_from: str
    email_use_tls: bool = True

    # Task Scheduler
    scheduler_check_interval_minutes: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
