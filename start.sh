#!/bin/bash
# Travel Weather Planner - Startup Script for Linux/Mac

echo "============================================================"
echo "🌍 Travel Weather Planner - Starting Server"
echo "============================================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source virtual/bin/activate"
    echo ""
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your OPENAI_API_KEY"
    echo ""
    exit 1
fi

echo "✓ Virtual environment: Active"
echo "✓ Configuration file: Found"
echo ""
echo "Starting server..."
echo "Open your browser to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
