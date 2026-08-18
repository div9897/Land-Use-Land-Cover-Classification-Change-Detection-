@echo off
echo.
echo ====================================
echo  LULC Classification Dashboard
echo  Quick Start Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install requirements
echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    echo Some dependencies may have installation issues - trying to continue anyway
)

REM Run Streamlit app
echo.
echo ====================================
echo  Starting LULC Dashboard...
echo ====================================
echo.
echo The dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py

pause
