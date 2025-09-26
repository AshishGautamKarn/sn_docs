@echo off
REM ServiceNow Advanced Visual Documentation - Windows Startup Script
REM This script automatically sets up and starts the ServiceNow documentation app

setlocal enabledelayedexpansion

echo ================================================
echo 🚀 ServiceNow Advanced Visual Documentation
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python is available
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    echo Please install pip first
    pause
    exit /b 1
)

echo [INFO] pip is available

REM Check if we're in the right directory
if not exist "enhanced_app.py" (
    echo [ERROR] This script must be run from the ServiceNow documentation project directory
    echo Please navigate to the project directory and run this script again
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [STEP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [STEP] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo [STEP] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [STEP] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

REM Setup environment file
if not exist ".env" (
    echo [STEP] Creating .env file from template...
    copy env.template .env
    echo [SUCCESS] Environment file created!
) else (
    echo [INFO] Environment file already exists
)

REM Initialize database
echo [STEP] Initializing database tables...
python -c "from database import initialize_database; db = initialize_database(); print('✅ Database tables created successfully!')"
if errorlevel 1 (
    echo [WARNING] Database initialization had issues, but app will still work
)

echo.
echo [SUCCESS] 🎉 Setup complete! All systems are ready.
echo.
echo 📱 Application URL: http://localhost:8506
echo 🗄️  Database: SQLite (default)
echo.
echo Press Ctrl+C to stop the application
echo.

REM Start the application
echo [STEP] Starting ServiceNow Documentation App...
streamlit run enhanced_app.py --server.port=8506 --server.address=0.0.0.0 --browser.gatherUsageStats=false

pause
