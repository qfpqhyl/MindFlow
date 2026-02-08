# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current Repository Reality (important)

- `CLAUDE.md`/README content was partially outdated; prefer the actual source tree over docs when they disagree.
- There is currently **no automated backend test suite file** in `backend/` and no configured frontend test runner script in `frontend/package.json`.
- A standalone service launcher exists at repo root: `start_services.sh` (starts backend/frontend, writes PID/log files under `logs/`).

## Common Development Commands

### Backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Useful backend checks:

```bash
# Service health
curl http://localhost:8000/health

# Open API docs
# http://localhost:8000/docs
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
npm run preview
```

Single-file linting:

```bash
cd frontend
npm run lint -- src/App.jsx
```

### Run both services together

```bash
# from repo root
bash ./start_services.sh
```

This script:
- starts backend on `8000` and frontend on `5173`
- records logs in `logs/backend.log` and `logs/frontend.log`
- stores PIDs in `logs/backend.pid` and `logs/frontend.pid`

## Tests (current status)

- **Backend:** no committed `test_*.py` test suite found in current tree.
- **Frontend:** `src/App.test.jsx` exists, but no `test` script/dependency is configured in `package.json`.
- Therefore there is currently no reliable “run all tests” or “run a single test” command in this repo state.

## Big-Picture Architecture

### System shape

- **Backend:** FastAPI app in `backend/main.py` with modular routers in `backend/app/api/*.py`.
- **Frontend:** React SPA in `frontend/src`, routed in `frontend/src/App.jsx`.
- **Persistence:** SQLite via a shared `Database` wrapper (`backend/app/database.py`) and global `db` instance.
- **AI:** NVIDIA-compatible chat completion integration via `backend/app/ai_service.py`.
- **Async jobs:** APScheduler-based reminder worker in `backend/app/scheduler.py`.

### Backend request lifecycle

1. `backend/main.py` app startup runs lifespan hooks:
   - initializes SQLite schema (`db.init_db()`)
   - starts scheduler (`task_scheduler.start()`)
2. Routers are mounted under `/api/v1`.
3. Most endpoints use JWT user identity from `get_current_user` dependency.
4. Database access consistently uses:
   - `with db.get_connection() as conn:`
   - automatic commit/rollback in context manager.

### Core backend domains

- `auth.py`: username/password auth and token issuance.
- `github_auth.py`: GitHub OAuth login/callback and account linking.
- `conversations.py` + `messages.py`: chat history and model interaction.
- `organize.py` + `documents.py`: convert chats into persisted docs and tags.
- `tasks.py` + `emails.py` + `scheduler.py`: task tracking and reminder notifications.
- `ai.py` + `user_settings` table: per-user default model selection.

### Streaming chat path (multi-file behavior)

- Frontend uses `messagesAPI.sendStream()` in `frontend/src/services/api.js`.
- Backend SSE endpoint is `POST /api/v1/conversations/{conversation_id}/messages/stream` in `backend/app/api/messages.py`.
- Flow:
  1. user message stored in `messages`
  2. full conversation history loaded
  3. AI stream yielded as SSE `event: chunk`
  4. assistant final response stored in `messages`
  5. SSE `event: complete` emitted

### Frontend architecture patterns

- `frontend/src/App.jsx` defines public routes (`/login`, GitHub callback) and protected app routes under `Layout`.
- Auth state is centralized in `frontend/src/contexts/AuthContext.jsx`.
- JWT + user snapshot are stored in `localStorage`.
- Axios interceptors in `frontend/src/services/api.js` inject bearer tokens and redirect to `/login` on 401.
- Frontend API base URL is currently hardcoded to `http://localhost:8000/api/v1` in `services/api.js`.
- Vite dev proxy (`frontend/vite.config.js`) proxies `/api` to backend, but current API client uses absolute base URL directly.

## Database shape (operationally important)

Defined in `backend/app/database.py`:
- `users` (supports password and GitHub OAuth identities)
- `conversations`, `messages`
- `documents`, `document_tags`
- `tasks`, `email_notifications`
- `user_settings`

Notable runtime coupling:
- scheduler updates `tasks.status` to `overdue` and sets `email_sent`
- default model preference is read from `user_settings.default_model_id`

## Config and environment

Backend config is in `backend/app/config.py` (`pydantic-settings`, `.env`):
- API host/port/prefix
- JWT settings
- NVIDIA API settings
- SMTP settings
- GitHub OAuth settings
- scheduler interval setting (currently scheduler code uses fixed 5-minute interval)

## External instruction files

- No `.cursorrules` or `.cursor/rules/*` found.
- No `.github/copilot-instructions.md` found.
