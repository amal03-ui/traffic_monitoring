@echo off
echo ================================================
echo System Requirements Check
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python is installed
    python --version
) else (
    echo ❌ Python is NOT installed
    echo Please install Python 3.10+ from https://python.org
)

echo.

:: Check Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git is installed
    git --version
) else (
    echo ❌ Git is NOT installed
    echo Please install Git from https://git-scm.com
)

echo.

:: Check if this is a git repository
if exist ".git" (
    echo ✅ This is a Git repository
) else (
    echo ⚠️ This is not a Git repository
)

echo.

:: Check virtual environment
if exist "venv" (
    echo ✅ Virtual environment exists
) else (
    echo ⚠️ Virtual environment not found
    echo Run setup.bat to create it
)

echo.

:: Check model file
if exist "model\yolov8n.pt" (
    echo ✅ YOLOv8n model exists
) else (
    echo ⚠️ YOLOv8n model not found
    echo Will be downloaded during setup
)

echo.
echo ================================================
echo Check completed!
echo ================================================
pause
