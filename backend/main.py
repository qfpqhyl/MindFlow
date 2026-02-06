"""
MindFlow Backend - Main Application
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import db
from app.scheduler import task_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MindFlow backend...")
    logger.info(f"Database: {settings.db_file}")

    # Initialize database
    db.init_db()
    logger.info("Database initialized")

    # Start task scheduler
    task_scheduler.start()
    logger.info("Task scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down MindFlow backend...")
    task_scheduler.stop()
    logger.info("Task scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="MindFlow API",
    description="MindFlow - 思流如潮，智能工作流应用 - 集成聊天、文档管理和定时任务",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "errors": [str(exc)]
        }
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MindFlow API",
        "version": "1.0.0"
    }


# API info
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MindFlow API",
        "version": "1.0.0",
        "description": "智能工作流应用 - 集成聊天、文档管理和定时任务",
        "docs": "/docs",
        "health": "/health"
    }


# Import and register routers
from app.api import auth, conversations, messages, organize, documents, tasks, users, emails, ai

# Register routers with API v1 prefix
api_prefix = settings.api_v1_prefix

app.include_router(auth.router, prefix=api_prefix, tags=["Authentication"])
app.include_router(conversations.router, prefix=api_prefix, tags=["Conversations"])
app.include_router(messages.router, prefix=api_prefix, tags=["Messages"])
app.include_router(organize.router, prefix=api_prefix, tags=["Organize"])
app.include_router(documents.router, prefix=api_prefix, tags=["Documents"])
app.include_router(tasks.router, prefix=api_prefix, tags=["Tasks"])
app.include_router(users.router, prefix=api_prefix, tags=["Users"])
app.include_router(emails.router, prefix=api_prefix, tags=["Email Notifications"])
app.include_router(ai.router, prefix=api_prefix, tags=["AI Configuration"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
