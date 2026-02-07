# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindFlow is an intelligent workflow application that integrates AI chat, knowledge management, and task reminders. It's built as a full-stack application with:

- **Backend**: FastAPI 0.115.0 with SQLite database
- **Frontend**: React 19.2 with Vite 7.2 and MUI v7
- **AI**: NVIDIA/MiniMax API integration (default: `minimaxai/minimax-m2.1`)
- **Email**: Feishu SMTP integration for task reminders

## Architecture

### Backend Structure

The backend follows a modular FastAPI architecture:

```
backend/
├── main.py                 # Application entry point, lifespan management
├── app/
│   ├── config.py           # Pydantic settings (loads from .env)
│   ├── database.py         # SQLite database initialization and utilities
│   ├── auth.py             # JWT token generation, password hashing
│   ├── dependencies.py     # FastAPI dependency injection (get_current_user)
│   ├── ai_service.py       # NVIDIA API integration
│   ├── email_service.py    # SMTP email sending
│   ├── scheduler.py        # APScheduler for task reminders
│   ├── schemas.py          # Pydantic models for request/response validation
│   └── api/                # API route modules (auth, conversations, messages, etc.)
```

**Key patterns:**
- All routes use `/api/v1` prefix
- JWT authentication via `get_current_user` dependency
- Database access through context manager pattern: `with db.get_connection() as conn:`
- UUID generation via `db.generate_uuid()`
- Global `db` instance imported from `app.database`

### Frontend Structure

The frontend uses React Router v7 with a protected route pattern:

```
frontend/src/
├── main.jsx                # React entry point
├── App.jsx                 # Router configuration with ProtectedRoute wrapper
├── theme.js                # MUI theme (black/white minimalist design)
├── components/
│   ├── Layout.jsx          # Main app layout with navigation
│   └── MarkdownRenderer.jsx  # Markdown rendering with syntax highlighting
├── contexts/
│   └── AuthContext.jsx     # Authentication state and token management
├── services/
│   └── api.js              # Axios instance with interceptors + API functions
└── pages/                  # Page components (ConversationsPage, ChatPage, etc.)
    ├── ChatPage.jsx         # Chat interface with streaming and markdown
    ├── ConversationsPage.jsx # Conversation list and management
    ├── DocumentsPage.jsx    # Document viewing and search
    ├── LoginPage.jsx        # Authentication (login/register)
    ├── SettingsPage.jsx     # User settings and AI model selection
    └── TasksPage.jsx        # Task management with due dates
```

**Key patterns:**
- Auth state stored in `localStorage` (token and user)
- Axios interceptors auto-inject JWT and handle 401 redirects
- Protected routes check `isAuthenticated` from AuthContext
- SSE streaming for AI responses via `messagesAPI.sendStream()`
- MUI v7 components with custom black/white theme
- Markdown rendering with `react-markdown` and syntax highlighting

### Database Schema

SQLite database with 8 tables:
- `users` - User accounts with bcrypt password hashes
- `conversations` - Chat conversations linked to users
- `messages` - Chat messages with role (user/assistant/system)
- `documents` - Generated documents from conversations
- `document_tags` - Tags for documents
- `tasks` - Tasks with due dates and reminder settings
- `email_notifications` - Email reminder history
- `user_settings` - User preferences (default model, email)

Database auto-initializes on first run at `./data/mindflow.db`.

## Development Commands

### Backend

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with NVIDIA_API_KEY and email settings

# Run development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run API tests
python test_api.py

# Direct Python execution
python main.py
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Running Both Services

Start backend on port 8000, then frontend on port 5173. Vite proxy handles `/api` requests to backend.

## Configuration

### Required Environment Variables (.env in backend/)

```env
# Database
DB_FILE=./data/mindflow.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_V1_PREFIX=/api/v1

# JWT Settings
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# NVIDIA/MiniMax API - REQUIRED for AI chat
NVIDIA_API_KEY=your-nvidia-api-key
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1/chat/completions
DEFAULT_MODEL=minimaxai/minimax-m2.1

# Email - Optional (for task reminders)
SMTP_HOST=smtp.feishu.cn
SMTP_PORT=465
SMTP_USERNAME=your-email@feishu.cn
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=your-email@feishu.cn

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Task Scheduler
SCHEDULER_CHECK_INTERVAL_MINUTES=5
```

Get NVIDIA API key from https://build.nvidia.com
Available models include MiniMax M2.1, Llama 3.1 405B, and others via NVIDIA API.

### Frontend Configuration

- API base URL: `http://localhost:8000/api/v1` (hardcoded in `services/api.js`)
- Vite dev server: `http://localhost:5173`
- Proxy configured in `vite.config.js`

## Key Implementation Details

### AI Service (`app/ai_service.py`)

- Wraps NVIDIA/MiniMax API for chat completions
- Supports streaming responses via async generator
- System prompt: "You are a helpful AI assistant."
- Returns chunks prefixed with content markers
- Additional helper methods: `generate_summary()`, `generate_document()`, `suggest_tags()`

### Streaming SSE Implementation

Backend (`app/api/messages.py`):
- Generates Server-Sent Events for AI streaming
- Events: `chunk`, `error`, `complete`
- Uses `yield` to send events asynchronously

Frontend (`services/api.js`):
- `sendStream()` function with callbacks: `onChunk`, `onComplete`, `onError`
- Parses SSE format: `event: type\ndata: JSON\n`
- Handles text decoder buffer for partial JSON

### Authentication Flow

1. User registers/logs in → returns JWT token + user data
2. Token stored in `localStorage`
3. Axios request interceptor adds `Authorization: Bearer <token>`
4. Response interceptor handles 401 → redirects to `/login`
5. Protected routes check `isAuthenticated` from AuthContext

### Task Scheduler

- APScheduler runs every 5 minutes (configurable)
- Checks for overdue tasks with `reminder_enabled=1`
- Sends email reminders via `email_service.py`
- Updates `email_sent` flag on tasks

### Document Organization

- `/api/v1/organize/to-document` endpoint converts conversations to documents
- AI generates summary and tags automatically
- Links to source conversation via `source_conversation_id`

### AI Model Configuration

- `/api/v1/ai/models` endpoint lists available AI models
- Users can set default model via `/api/v1/ai/set-default`
- Model preference stored in `user_settings` table
- Frontend SettingsPage allows model selection UI
- Supported models: MiniMax M2.1, Llama 3.1 405B, and other NVIDIA-hosted models

### API Endpoints Structure

All routes use `/api/v1` prefix. Main endpoint groups:

- **Authentication** (`/auth/*`): register, login, refresh token
- **Conversations** (`/conversations`): CRUD operations for chat conversations
- **Messages** (`/conversations/{id}/messages`): send messages, stream responses
- **Documents** (`/documents`): create, view, search, and delete documents
- **Tasks** (`/tasks`): create, update, complete tasks, send reminders
- **Organize** (`/organize/*`): convert conversations to documents, get suggestions
- **AI** (`/ai/*`): list available models, set user's default model
- **Users** (`/users/*`): get user profile, update settings
- **Email Notifications** (`/emails`): view email notification history

Interactive API documentation available at `/docs` (Swagger UI) when running backend.

## Testing

Backend includes `test_api.py` which exercises:
- Health check
- User registration/login
- Creating conversations
- Sending messages
- Creating documents
- Creating tasks

Run with `python test_api.py` after starting the backend server.

## Deployment Notes

### Security Checklist

Before deploying to production:
1. Change `SECRET_KEY` in `.env` to a strong random value
2. Update `CORS_ORIGINS` to actual frontend domain
3. Use environment variables for all secrets
4. Enable HTTPS
5. Set proper file permissions on database
6. Consider using PostgreSQL instead of SQLite for production

### Database Backups

SQLite database at `backend/data/mindflow.db` - backup this file regularly.

## Common Issues

- **NVIDIA API 401 error**: Check `NVIDIA_API_KEY` in `.env`
- **Email sending fails**: Verify SMTP credentials and Feishu SMTP settings
- **Frontend can't reach backend**: Ensure backend is running on port 8000
- **Database errors**: Delete `mindflow.db` and restart to reinitialize
- **CORS errors**: Check `CORS_ORIGINS` in backend config
- **AI model not responding**: Verify `DEFAULT_MODEL` is supported by NVIDIA API

## Adding New Features

### New API Endpoint

1. Add Pydantic schemas in `app/schemas.py`
2. Create route in `app/api/` module
3. Register router in `main.py`
4. Add frontend API functions in `services/api.js`
5. Build UI components as needed

### New Database Table

1. Add `CREATE TABLE` in `app/database.py:init_db()`
2. Create indexes for frequently queried columns
3. Add Pydantic model in `schemas.py`
4. Implement CRUD operations in appropriate API module
