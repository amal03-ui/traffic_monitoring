@echo off
echo ================================================
echo Advanced Traffic Monitoring System - Starting Server
echo ================================================
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

:: Activate virtual environment and start server
echo 🚀 Starting Flask server...
echo.
echo Server will be available at:
echo 🌐 http://localhost:5000
echo 🌐 http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

call .\venv\Scripts\activate.bat
.\venv\Scripts\python.exe backend\main.py
