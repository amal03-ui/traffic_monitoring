@echo off
echo ================================================
echo Advanced Traffic Monitoring System - Setup
echo ================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created
echo.

:: Activate virtual environment and install dependencies
echo 📥 Installing dependencies...
call .\venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

:: Download YOLOv8n model if not exists
if not exist "model\yolov8n.pt" (
    echo 🤖 Downloading YOLOv8n model...
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
    if exist "yolov8n.pt" (
        move yolov8n.pt model\
        echo ✅ Model downloaded and moved to model directory
    )
) else (
    echo ✅ YOLOv8n model already exists
)

echo.
echo ================================================
echo 🎉 Setup completed successfully!
echo ================================================
echo.
echo To run the application:
echo 1. Run: start_server.bat
echo 2. Open browser: http://localhost:5000
echo.
echo Press any key to continue...
pause >nul
