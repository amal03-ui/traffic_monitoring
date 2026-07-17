# Advanced Traffic Monitoring System - Start Server

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Advanced Traffic Monitoring System - Starting Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Start server
Write-Host "🚀 Starting Flask server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor White
Write-Host "🌐 http://localhost:5000" -ForegroundColor Yellow
Write-Host "🌐 http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host ""

& .\venv\Scripts\Activate.ps1
& .\venv\Scripts\python.exe backend\main.py
