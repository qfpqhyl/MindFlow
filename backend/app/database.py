"""
Database models for MindFlow
"""
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path
from app.config import get_settings

settings = get_settings()


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.db_file
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    github_id TEXT UNIQUE,
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                );

                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    summary TEXT,
                    source_conversation_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (source_conversation_id) REFERENCES conversations(conversation_id)
                );

                CREATE TABLE IF NOT EXISTS document_tags (
                    tag_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    tag_name TEXT NOT NULL,
                    FOREIGN KEY (document_id) REFERENCES documents(document_id)
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'overdue')),
                    reminder_enabled BOOLEAN DEFAULT 1,
                    reminder_email TEXT,
                    source_document_id TEXT,
                    email_sent BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (source_document_id) REFERENCES documents(document_id)
                );

                CREATE TABLE IF NOT EXISTS email_notifications (
                    notification_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    recipient_email TEXT NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('sent', 'failed', 'pending')),
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                );

                CREATE TABLE IF NOT EXISTS user_settings (
                    setting_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    default_email TEXT,
                    reminder_enabled BOOLEAN DEFAULT 1,
                    default_model_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
                CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
                CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            """)

    def generate_uuid(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())


# Global database instance
db = Database()
