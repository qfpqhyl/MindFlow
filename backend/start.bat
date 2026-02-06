@echo off
REM MindFlow Backend Startup Script for Windows

echo 🚀 Starting MindFlow Backend...

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create data directory if it doesn't exist
if not exist "data" (
    echo 📁 Creating data directory...
    mkdir data
)

REM Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before running the server!
)

REM Start the server
echo.
echo ✅ Setup complete!
echo.
echo 🌟 Starting MindFlow API server...
echo 📍 API will be available at: http://localhost:8000
echo 📚 API documentation: http://localhost:8000/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
