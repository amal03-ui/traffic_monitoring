# Advanced Traffic Monitoring System - PowerShell Setup Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Advanced Traffic Monitoring System - Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
try {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Activate virtual environment and install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
try {
    & .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Download YOLOv8n model if not exists
if (-not (Test-Path "model\yolov8n.pt")) {
    Write-Host "🤖 Downloading YOLOv8n model..." -ForegroundColor Yellow
    try {
        python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
        if (Test-Path "yolov8n.pt") {
            Move-Item "yolov8n.pt" "model\"
            Write-Host "✅ Model downloaded and moved to model directory" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Model download failed, will download automatically on first run" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ YOLOv8n model already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the application:" -ForegroundColor White
Write-Host "1. Run: .\start_server.ps1" -ForegroundColor Yellow
Write-Host "2. Open browser: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"
