#!/bin/bash

# MindFlow Backend Startup Script

echo "🚀 Starting MindFlow Backend..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the server!"
fi

# Start the server
echo ""
echo "✅ Setup complete!"
echo ""
echo "🌟 Starting MindFlow API server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
