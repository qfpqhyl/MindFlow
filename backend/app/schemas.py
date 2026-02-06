"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# Response schemas
class APIResponse(BaseModel):
    """Standard API response"""
    code: int
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response"""
    code: int
    message: str
    errors: Optional[List[str]] = None


# Auth schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    user_id: str
    username: str
    token: str


class RefreshTokenResponse(BaseModel):
    token: str


# User schemas
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime
    settings: Optional[dict] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


# Conversation schemas
class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0


class ConversationDetail(ConversationResponse):
    messages: List[dict] = []


# Message schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    stream: bool = False


class MessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    created_at: datetime


class MessageSendResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse


# Document schemas
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    summary: Optional[str] = None
    tags: List[str] = []


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    summary: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentResponse):
    content: str
    source_conversation_id: Optional[str] = None


# Organize schemas
class OrganizeToDocument(BaseModel):
    conversation_id: str
    title: str
    summary: Optional[str] = None
    create_task: bool = False
    task_config: Optional['TaskConfig'] = None


class TaskConfig(BaseModel):
    due_date: datetime
    reminder_enabled: bool = True
    reminder_email: Optional[EmailStr] = None


class OrganizeResponse(BaseModel):
    document_id: str
    document_url: str
    task_id: Optional[str] = None
    task_url: Optional[str] = None


class OrganizeSuggestionsResponse(BaseModel):
    summary: str
    suggested_title: str
    key_points: List[str]
    suggested_tags: List[str]


# Task schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: datetime
    reminder_enabled: bool = True
    reminder_email: Optional[EmailStr] = None
    source_document_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(pending|completed)$")
    reminder_enabled: Optional[bool] = None
    reminder_email: Optional[EmailStr] = None


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    status: str
    reminder_enabled: bool
    reminder_email: Optional[EmailStr] = None
    source_document_id: Optional[str] = None
    created_at: datetime


class TaskDetail(TaskResponse):
    email_sent: bool
    updated_at: datetime


class TaskCompleteResponse(BaseModel):
    task_id: str
    status: str
    completed_at: datetime


class TaskReminderResponse(BaseModel):
    task_id: str
    email_sent: bool
    sent_at: datetime


# Email notification schemas
class EmailNotificationResponse(BaseModel):
    notification_id: str
    task_id: str
    task_title: str
    recipient_email: str
    status: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class EmailSettingsUpdate(BaseModel):
    default_email: EmailStr
    reminder_enabled: bool = True


# AI Model schemas
class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str = "nvidia"
    description: Optional[str] = None


class ModelsListResponse(BaseModel):
    models: List[ModelInfo]


class SetDefaultModel(BaseModel):
    model_id: str


# Pagination
class PaginatedResponse(BaseModel):
    total: int
    page: int = 1
    page_size: int = 20
    items: List[dict]
