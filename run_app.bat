@echo off
REM Calgary to Zhongshan Travel Planner - Application Launcher
REM This script starts the Streamlit application

echo.
echo ========================================
echo  Calgary to Zhongshan Travel Planner
echo  Starting Application...
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "main.py" (
    echo ❌ ERROR: main.py not found!
    echo Please run this script from the application directory.
    echo Expected location: calgary_zhongshan_travel_app\
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please run setup_check.bat first to verify installation.
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Streamlit is not installed
    echo Please run setup_check.bat to install required packages.
    pause
    exit /b 1
)

REM Create data directory if it doesn't exist
if not exist "data" (
    echo 📁 Creating data directory...
    mkdir data
)

REM Display startup information
echo ✅ Python and Streamlit are ready
echo 📁 Application directory: %CD%
echo 🗄️  Database location: %CD%\data\travel_planner.db
echo.

REM Check if port 8501 is available
netstat -an | find "8501" | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  WARNING: Port 8501 appears to be in use
    echo The application may start on a different port
    echo.
)

echo 🚀 Starting Calgary to Zhongshan Travel Planner...
echo.
echo 🌐 The application will open in your default web browser
echo 📍 Default URL: http://localhost:8501
echo.
echo ⏹️  To stop the application: Press Ctrl+C in this window
echo 🔄 To restart: Close this window and run run_app.bat again
echo.
echo ========================================
echo.

REM Start the Streamlit application
echo Starting Streamlit server...
echo.

REM Run with specific configuration for better Windows compatibility
streamlit run main.py ^
    --server.port 8501 ^
    --server.address localhost ^
    --server.headless false ^
    --browser.gatherUsageStats false ^
    --server.enableCORS false ^
    --server.enableXsrfProtection false

REM If we reach here, the application has stopped
echo.
echo ========================================
echo  Application Stopped
echo ========================================
echo.
echo The Calgary to Zhongshan Travel Planner has been stopped.
echo.
echo 🔄 To restart the application, run this script again
echo 📖 For help, see SETUP_GUIDE.md
echo.

pause

