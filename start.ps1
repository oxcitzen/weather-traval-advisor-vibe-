# Travel Weather Planner - Startup Script for Windows
# Run this script to start the web application

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "🌍 Travel Weather Planner - Starting Server" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "Please run: .\virtual\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "✓ Virtual environment: Active" -ForegroundColor Green
Write-Host "✓ Configuration file: Found" -ForegroundColor Green
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Cyan
Write-Host "Open your browser to: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the FastAPI server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
